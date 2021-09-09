from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.list import blueprint
from application.models import (Category, Item, List, ListCategory, ListItem,
                                ListItemType)


def warn_unchecked_categories(list_id):
    # checked categories in the list
    checked_categories = database.session.query(Category.category_id).join(
        ListCategory,
        and_(
            ListCategory.category_id == Category.category_id,
            ListCategory.list_id == list_id,
        ),
    )

    # for the checked items in the list, find the unchecked categories
    unchecked_categories = (
        database.session.query(Category)
        .join(Item)
        .join(
            ListItem,
            and_(ListItem.item_id == Item.item_id, ListItem.list_id == list_id),
        )
        .filter(Category.category_id.notin_(checked_categories))
        .order_by(Category.name)
    )

    # warn about unchecked categories for checked items
    for category in unchecked_categories:
        flash(
            "Some items are not visible. "
            + f"The category '{category.name}' should be selected.",
            "warning",
        )


@blueprint.route("/item/<int:list_id>")
@login_required
def item(list_id):
    list_ = List.query.get(list_id)
    if list_ is None:
        return redirect(url_for("list.list"))

    warn_unchecked_categories(list_id)

    items_categories = (
        database.session.query(Item, Category, ListItem)
        .join(Category)
        .join(
            ListCategory,
            and_(
                ListCategory.category_id == Category.category_id,
                ListCategory.list_id == list_id,
            ),
        )
        .outerjoin(
            ListItem,
            and_(ListItem.item_id == Item.item_id, ListItem.list_id == list_id),
        )
        .order_by(Category.name, Item.name)
        .all()
    )

    return render_template(
        "list/item/item.html.jinja",
        title="Items in List",
        list=list_,
        items_categories=items_categories,
        cancel=url_for("list.list"),
    )


@blueprint.route("/item/switch_type", methods=["POST"])
@login_required
def item_switch_type():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
        version_id = data.get("version_id")
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    try:
        list_item = ListItem.query.get((list_id, item_id))
        if list_item is None:
            if version_id != "none":
                raise StaleDataError()

            list_item = ListItem(
                list_id=list_id, item_id=item_id, type_=ListItemType.selection
            )
            database.session.add(list_item)
        else:
            if version_id != list_item.version_id:
                raise StaleDataError()

            list_item.type_ = list_item.type_.next()
            if list_item.type_ == ListItemType.none:
                database.session.delete(list_item)

        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "type": list_item.type_.name,
                "version": list_item.version_id,
            }
        )
    except (IntegrityError, StaleDataError):
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify({"status": "cancel", "url": url_for("list.list")})

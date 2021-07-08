from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_

from application import database
from application.list import blueprint
from application.models import (Category, Item, List, ListItem, ListItemType,
                                list_category)


def warn_unchecked_categories(list_id):
    # checked categories in the list
    checked_categories = database.session.query(Category.category_id).join(
        list_category,
        and_(
            list_category.c.category_id == Category.category_id,
            list_category.c.list_id == list_id,
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
            list_category,
            and_(
                list_category.c.category_id == Category.category_id,
                list_category.c.list_id == list_id,
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


@blueprint.route("/item/check", methods=["POST"])
@login_required
def item_check():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    list_ = List.query.get(list_id)
    item = Item.query.get(item_id)

    if list_ is None or item is None:
        return jsonify({"status": "invalid data"}), 400

    # TODO: review this
    list_item = ListItem(type_=ListItemType.checked, checked=True)
    list_item.item = item
    with database.session.no_autoflush:
        list_.items.append(list_item)
    database.session.commit()

    return jsonify({"status": "ok"})


@blueprint.route("/item/uncheck", methods=["POST"])
@login_required
def item_uncheck():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    list_ = List.query.get(list_id)
    item = Item.query.get(item_id)

    if list_ is None or item is None:
        return jsonify({"status": "invalid data"}), 400

    # TODO: review this
    list_item = ListItem.query.get((list_id, item_id))
    database.session.delete(list_item)
    database.session.commit()

    return jsonify({"status": "ok"})


@blueprint.route("/item/get")
@login_required
def item_get():
    try:
        list_id = int(request.args.get("list_id"))
        item_id = int(request.args.get("item_id"))
    except (TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    # TODO: review this (does it still work?)
    if (
        Item.query.join(
            ListItem, and_(ListItem.item_id == Item.item_id, Item.item_id == item_id)
        )
        .join(List, and_(ListItem.list_id == List.list_id, List.list_id == list_id))
        .first()
    ):
        return jsonify({"status": "checked"})
    else:
        return jsonify({"status": "unchecked"})

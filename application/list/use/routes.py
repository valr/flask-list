from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.list import blueprint
from application.models import Category, Item, List, ListItem


@blueprint.route("/use/<int:list_id>")
@login_required
def use(list_id):
    list_ = List.query.get(list_id)
    if list_ is None:
        return redirect(url_for("list.list"))

    categories_items = (
        database.session.query(Category, Item, ListItem)
        .select_from(Item)
        .join(Category)
        .join(
            ListItem,
            and_(ListItem.item_id == Item.item_id, ListItem.list_id == list_id),
        )
        .order_by(Category.name, Item.name)
        .all()
    )

    return render_template(
        "list/use/list.html.jinja",
        title="List",
        list=list_,
        categories_items=categories_items,
        cancel_url=url_for("list.list"),
    )


@blueprint.route("/item/switch_selection", methods=["POST"])
@login_required
def item_switch_selection():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
        version_id = data.get("version_id")
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    try:
        list_item = ListItem.query.get((list_id, item_id))
        if list_item is None or list_item.version_id != version_id:
            raise StaleDataError()

        list_item.selection = not list_item.selection
        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "selection": list_item.selection,
                "version": list_item.version_id,
            }
        )
    except (IntegrityError, StaleDataError):
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify({"status": "cancel", "cancel_url": url_for("list.list")})

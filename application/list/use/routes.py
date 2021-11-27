from decimal import Decimal, DecimalException
from traceback import format_exc

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.list import blueprint
from application.models import Category, Item, List, ListItem, ListItemType


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
        .filter(ListItem.type_ != ListItemType.none)
        .filter(
            or_(
                current_user.filter_ == Category.filter_,
                current_user.filter_ == None,  # noqa: E711
            )
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
        print(format_exc())
        print(f"data: {data}")
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
        return jsonify(
            {"status": "cancel", "cancel_url": url_for("list.use", list_id=list_id)}
        )


@blueprint.route("/item/set_text", methods=["POST"])
@login_required
def item_set_text():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
        version_id = data.get("version_id")
        text = data.get("text")
    except (AttributeError, TypeError, ValueError):
        print(format_exc())
        print(f"data: {data}")
        return jsonify({"status": "missing or invalid data"}), 400

    try:
        list_item = ListItem.query.get((list_id, item_id))
        if list_item is None or list_item.version_id != version_id:
            raise StaleDataError()

        list_item.text = text
        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "version": list_item.version_id,
                # the text is not returned (it's already in the input element)
            }
        )
    except (IntegrityError, StaleDataError):
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify(
            {"status": "cancel", "cancel_url": url_for("list.use", list_id=list_id)}
        )


@blueprint.route("/item/set_number", methods=["POST"])
@login_required
def item_set_number():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
        version_id = data.get("version_id")
        number = Decimal(data.get("number"))
        to_add = Decimal(data.get("to_add", "0"))
    except (AttributeError, TypeError, ValueError, DecimalException):
        print(format_exc())
        print(f"data: {data}")
        return jsonify({"status": "missing or invalid data"}), 400

    try:
        list_item = ListItem.query.get((list_id, item_id))
        if list_item is None or list_item.version_id != version_id:
            raise StaleDataError()

        list_item.number = number + to_add
        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "number": str(list_item.number),
                "version": list_item.version_id,
            }
        )
    except (IntegrityError, StaleDataError):
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify(
            {"status": "cancel", "cancel_url": url_for("list.use", list_id=list_id)}
        )

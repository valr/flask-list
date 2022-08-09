from decimal import Decimal, DecimalException
from traceback import format_exc

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.item import blueprint
from application.item.forms import CreateForm, DeleteForm, UpdateForm
from application.models import Category, Item, ItemType


@blueprint.route("/create/<int:category_id>", methods=["GET", "POST"])
@login_required
def create(category_id):
    category = Category.query.get(category_id)
    if category is None or not current_user.has_access(category.list_):
        flash("The category has not been found.", "error")
        return redirect(url_for("list.read"))
    list_id = category.list_id

    form = CreateForm()
    form.category_id.choices = [
        (c.category_id, c.name)
        for c in Category.query.filter(Category.list_id == list_id).order_by(
            Category.name
        )
    ]
    form.type_.choices = [(type_.value, type_.name.title()) for type_ in ItemType]
    if form.validate_on_submit():
        try:
            item = Item(
                name=form.name.data,
                type_=ItemType(form.type_.data).name,
                selection=False,
                number=0,
                text="",
                category_id=form.category_id.data,
            )
            database.session.add(item)
            database.session.commit()
            flash("The item has been created.")
        except IntegrityError:
            database.session.rollback()
            flash(
                "The item has not been created due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.detail", list_id=list_id))
    elif request.method == "GET":
        form.category_id.data = category_id
        form.type_.data = ItemType.selection.value

    return render_template(
        "item/create.html.jinja",
        title="Create Item",
        form=form,
        cancel_url=url_for("list.detail", list_id=list_id),
    )


@blueprint.route("/update/<int:item_id>", methods=["GET", "POST"])
@login_required
def update(item_id):
    item = Item.query.get(item_id)
    if item is None or not current_user.has_access(item.category.list_):
        flash("The item has not been found.", "error")
        return redirect(url_for("list.read"))
    list_id = item.category.list_id

    form = UpdateForm(item.category_id, item.name)
    form.category_id.choices = [
        (c.category_id, c.name)
        for c in Category.query.filter(Category.list_id == list_id).order_by(
            Category.name
        )
    ]
    form.type_.choices = [(type_.value, type_.name.title()) for type_ in ItemType]
    if form.validate_on_submit():
        try:
            if item.version_id != form.version_id.data:
                raise StaleDataError()

            item.name = form.name.data
            item.category_id = form.category_id.data
            item.type_ = ItemType(form.type_.data).name
            database.session.commit()
            flash("The item has been updated.")
        except (IntegrityError, StaleDataError):
            database.session.rollback()
            flash(
                "The item has not been updated due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.detail", list_id=list_id))
    elif request.method == "GET":
        form.name.data = item.name
        form.category_id.data = item.category_id
        form.type_.data = item.type_.value
        form.version_id.data = item.version_id

    return render_template(
        "item/update.html.jinja",
        title="Update Item",
        form=form,
        cancel_url=url_for("list.detail", list_id=list_id),
    )


@blueprint.route("/delete/<int:item_id>", methods=["GET", "POST"])
@login_required
def delete(item_id):
    item = Item.query.get(item_id)
    if item is None or not current_user.has_access(item.category.list_):
        flash("The item has not been found.", "error")
        return redirect(url_for("list.read"))
    list_id = item.category.list_id

    form = DeleteForm()
    form.type_.choices = [(type_.value, type_.name.title()) for type_ in ItemType]
    if form.validate_on_submit():
        try:
            if item.version_id != form.version_id.data:
                raise StaleDataError()

            database.session.delete(item)
            database.session.commit()
            flash("The item has been deleted.")
        except StaleDataError:
            database.session.rollback()
            flash(
                "The item has not been deleted due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.detail", list_id=list_id))
    elif request.method == "GET":
        form.name.data = item.name
        form.category_name.data = item.category.name
        form.type_.data = item.type_.value
        form.version_id.data = item.version_id

    return render_template(
        "item/delete.html.jinja",
        title="Delete Item",
        form=form,
        cancel_url=url_for("list.detail", list_id=list_id),
    )


@blueprint.route("switch_selection", methods=["POST"])
@login_required
def switch_selection():
    try:
        data = request.get_json(False, True, False)
        item_id = int(data.get("item_id"))
        version_id = data.get("version_id")
    except (AttributeError, TypeError, ValueError):
        print(format_exc())
        print(f"data: {data}")
        return jsonify({"status": "missing or invalid data"}), 400

    item = Item.query.get(item_id)
    if item is None or not current_user.has_access(item.category.list_):
        flash("The item has not been found.", "error")
        return jsonify({"status": "cancel", "cancel_url": url_for("list.read")})
    list_id = item.category.list_id

    try:
        if item.version_id != version_id:
            raise StaleDataError()

        item.selection = not item.selection
        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "selection": item.selection,
                "version": item.version_id,
            }
        )
    except StaleDataError:
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify(
            {"status": "cancel", "cancel_url": url_for("list.detail", list_id=list_id)}
        )


@blueprint.route("set_number", methods=["POST"])
@login_required
def set_number():
    try:
        data = request.get_json(False, True, False)
        item_id = int(data.get("item_id"))
        version_id = data.get("version_id")
        number = Decimal(data.get("number"))
        to_add = Decimal(data.get("to_add", "0"))
    except (AttributeError, TypeError, ValueError, DecimalException):
        print(format_exc())
        print(f"data: {data}")
        return jsonify({"status": "missing or invalid data"}), 400

    item = Item.query.get(item_id)
    if item is None or not current_user.has_access(item.category.list_):
        flash("The item has not been found.", "error")
        return jsonify({"status": "cancel", "cancel_url": url_for("list.read")})
    list_id = item.category.list_id

    try:
        if item.version_id != version_id:
            raise StaleDataError()

        item.number = number + to_add
        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "number": str(item.number),
                "version": item.version_id,
            }
        )
    except StaleDataError:
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify(
            {"status": "cancel", "cancel_url": url_for("list.detail", list_id=list_id)}
        )


@blueprint.route("set_text", methods=["POST"])
@login_required
def set_text():
    try:
        data = request.get_json(False, True, False)
        item_id = int(data.get("item_id"))
        version_id = data.get("version_id")
        text = data.get("text")
    except (AttributeError, TypeError, ValueError):
        print(format_exc())
        print(f"data: {data}")
        return jsonify({"status": "missing or invalid data"}), 400

    item = Item.query.get(item_id)
    if item is None or not current_user.has_access(item.category.list_):
        flash("The item has not been found.", "error")
        return jsonify({"status": "cancel", "cancel_url": url_for("list.read")})
    list_id = item.category.list_id

    try:
        if item.version_id != version_id:
            raise StaleDataError()

        item.text = text
        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "version": item.version_id,
                # the text is not returned (it's already in the input element)
            }
        )
    except StaleDataError:
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify(
            {"status": "cancel", "cancel_url": url_for("list.detail", list_id=list_id)}
        )

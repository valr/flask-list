from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.item import blueprint
from application.item.forms import CreateForm, DeleteForm, UpdateForm
from application.models import Category, Item


@blueprint.route("/create/<int:category_id>", methods=["GET", "POST"])
@login_required
def create(category_id):
    form = CreateForm()
    form.category_id.choices = [
        (c.category_id, c.name) for c in Category.query.order_by(Category.name)
    ]

    if form.validate_on_submit():
        try:
            item = Item(name=form.name.data, category_id=form.category_id.data)
            database.session.add(item)
            database.session.commit()
            flash("The item has been created.")
        except IntegrityError:
            database.session.rollback()
            flash(
                "The item has not been created due to concurrent modification.",
                "error",
            )

        return redirect(url_for("item.list"))
    elif request.method == "GET":
        form.category_id.data = category_id

    return render_template(
        "item/create.html.jinja",
        title="Create Item",
        form=form,
        cancel=url_for("item.list"),
    )


@blueprint.route("/update/<int:item_id>", methods=["GET", "POST"])
@login_required
def update(item_id):
    item = Item.query.get(item_id)
    if item is None:
        flash("The item has not been found.", "error")
        return redirect(url_for("item.list"))

    form = UpdateForm(item.name, item.category_id)
    form.category_id.choices = [
        (c.category_id, c.name) for c in Category.query.order_by(Category.name)
    ]

    if form.validate_on_submit():
        if form.version_id.data != str(item.version_id):
            flash(
                "The item has not been updated due to concurrent modification.",
                "error",
            )
            return redirect(url_for("item.list"))

        try:
            item.name = form.name.data
            item.category_id = form.category_id.data
            database.session.commit()
            flash("The item has been updated.")
        except (IntegrityError, StaleDataError):
            database.session.rollback()
            flash(
                "The item has not been updated due to concurrent modification.",
                "error",
            )

        return redirect(url_for("item.list"))
    elif request.method == "GET":
        form.version_id.data = item.version_id
        form.name.data = item.name
        form.category_id.data = item.category_id

    return render_template(
        "item/update.html.jinja",
        title="Update Item",
        form=form,
        cancel=url_for("item.list"),
    )


@blueprint.route("/delete/<int:item_id>", methods=["GET", "POST"])
@login_required
def delete(item_id):
    item = Item.query.get(item_id)
    if item is None:
        flash("The item has not been found.", "error")
        return redirect(url_for("item.list"))

    form = DeleteForm()
    form.category_id.choices = [
        (c.category_id, c.name) for c in Category.query.order_by(Category.name)
    ]

    if form.validate_on_submit():
        if form.version_id.data != str(item.version_id):
            flash(
                "The item has not been deleted due to concurrent modification.",
                "error",
            )
            return redirect(url_for("item.list"))

        try:
            database.session.delete(item)
            database.session.commit()
            flash("The item has been deleted.")
        except StaleDataError:
            database.session.rollback()
            flash(
                "The item has not been deleted due to concurrent modification.",
                "error",
            )

        return redirect(url_for("item.list"))
    elif request.method == "GET":
        form.version_id.data = item.version_id
        form.name.data = item.name
        form.category_id.data = item.category_id

    return render_template(
        "item/delete.html.jinja",
        title="Delete Item",
        form=form,
        cancel=url_for("item.list"),
    )


@blueprint.route("/list")
@login_required
def list():
    categories_items = (
        database.session.query(Category, Item)
        .outerjoin(Item)
        .order_by(Category.name, Item.name)
        .all()
    )

    return render_template(
        "item/list.html.jinja", title="Item", categories_items=categories_items
    )

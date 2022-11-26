from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, literal_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from flask_list import database
from flask_list.category import blueprint
from flask_list.category.forms import CreateForm, DeleteForm, UpdateForm
from flask_list.models import Category, Item, List


@blueprint.route("/create/<int:list_id>", methods=["GET", "POST"])
@login_required
def create(list_id):
    list_ = List.query.get(list_id)
    if list_ is None or not current_user.has_access(list_):
        flash("The list has not been found.", "error")
        return redirect(url_for("list.read"))

    form = CreateForm(list_id)
    if form.validate_on_submit():
        try:
            category = Category(name=form.name.data, list_id=list_id)
            database.session.add(category)
            database.session.commit()
            flash("The category has been created.")
        except IntegrityError:
            database.session.rollback()
            flash(
                "The category has not been created due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.detail", list_id=list_id))

    return render_template(
        "category/create.html.jinja",
        title="Create Category",
        form=form,
        cancel_url=url_for("list.detail", list_id=list_id),
    )


@blueprint.route("/update/<int:category_id>", methods=["GET", "POST"])
@login_required
def update(category_id):
    category = Category.query.get(category_id)
    if category is None or not current_user.has_access(category.list_):
        flash("The category has not been found.", "error")
        return redirect(url_for("list.read"))
    list_id = category.list_id

    form = UpdateForm(category.list_id, category.name)
    if form.validate_on_submit():
        try:
            if category.version_id != form.version_id.data:
                raise StaleDataError()

            category.name = form.name.data
            database.session.commit()
            flash("The category has been updated.")
        except (IntegrityError, StaleDataError):
            database.session.rollback()
            flash(
                "The category has not been updated due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.detail", list_id=list_id))
    elif request.method == "GET":
        form.name.data = category.name
        form.version_id.data = category.version_id

    return render_template(
        "category/update.html.jinja",
        title="Update Category",
        form=form,
        cancel_url=url_for("list.detail", list_id=list_id),
    )


@blueprint.route("/delete/<int:category_id>", methods=["GET", "POST"])
@login_required
def delete(category_id):
    category = Category.query.get(category_id)
    if category is None or not current_user.has_access(category.list_):
        flash("The category has not been found.", "error")
        return redirect(url_for("list.read"))
    list_id = category.list_id

    form = DeleteForm()
    if form.validate_on_submit():
        try:
            if category.version_id != form.version_id.data:
                raise StaleDataError()

            database.session.query(Item).filter(Item.category_id == category_id).delete(
                synchronize_session=False
            )

            database.session.query(Category).filter(
                Category.category_id == category_id
            ).delete(synchronize_session=False)

            database.session.commit()
            flash("The category has been deleted.")
        except StaleDataError:
            database.session.rollback()
            flash(
                "The category has not been deleted due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.detail", list_id=list_id))
    elif request.method == "GET":
        form.name.data = category.name
        form.version_id.data = category.version_id

    item_count = (
        database.session.query(func.count(literal_column("*")))
        .filter(Item.category_id == category_id)
        .scalar()
    )

    return render_template(
        "category/delete.html.jinja",
        title="Delete Category",
        form=form,
        item_count=item_count,
        cancel_url=url_for("list.detail", list_id=list_id),
    )

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.category import blueprint
from application.category.forms import CreateForm, DeleteForm, UpdateForm
from application.models import Category


@blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        try:
            category = Category(name=form.name.data)
            database.session.add(category)
            database.session.commit()
            flash("The category has been created.")
        except IntegrityError:
            database.session.rollback()
            flash(
                "The category has not been created "
                + "due to concurrent modification.",
                "error",
            )

        return redirect(url_for("category.list"))

    return render_template(
        "category/create.html.jinja",
        title="Create Category",
        form=form,
        cancel=url_for("category.list"),
    )


@blueprint.route("/update/<int:category_id>", methods=["GET", "POST"])
@login_required
def update(category_id):
    category = Category.query.get(category_id)
    if category is None:
        flash("The category has not been found.", "error")
        return redirect(url_for("category.list"))

    form = UpdateForm(category.name)
    if form.validate_on_submit():
        if form.version_id.data != str(category.version_id):
            flash(
                "The category has not been updated "
                + "due to concurrent modification.",
                "error",
            )
            return redirect(url_for("category.list"))

        try:
            category.name = form.name.data
            database.session.commit()
            flash("The category has been updated.")
        except (IntegrityError, StaleDataError):
            database.session.rollback()
            flash(
                "The category has not been updated "
                + "due to concurrent modification.",
                "error",
            )

        return redirect(url_for("category.list"))
    elif request.method == "GET":
        form.version_id.data = category.version_id
        form.name.data = category.name

    return render_template(
        "category/update.html.jinja",
        title="Update Category",
        form=form,
        cancel=url_for("category.list"),
    )


@blueprint.route("/delete/<int:category_id>", methods=["GET", "POST"])
@login_required
def delete(category_id):
    category = Category.query.get(category_id)
    if category is None:
        flash("The category has not been found.", "error")
        return redirect(url_for("category.list"))

    form = DeleteForm()
    if form.validate_on_submit():
        if form.version_id.data != str(category.version_id):
            flash(
                "The category has not been deleted "
                + "due to concurrent modification.",
                "error",
            )
            return redirect(url_for("category.list"))

        try:
            database.session.delete(category)
            database.session.commit()
            flash("The category has been deleted.")
        except IntegrityError:
            # in case of deletion, sqlalchemy will try setting the foreign key
            # of related items to null, resulting into an integrity error
            database.session.rollback()
            flash(
                "The category has not been deleted "
                + "because it still contains item(s).",
                "error",
            )
        except StaleDataError:
            database.session.rollback()
            flash(
                "The category has not been deleted "
                + "due to concurrent modification.",
                "error",
            )

        return redirect(url_for("category.list"))
    elif request.method == "GET":
        form.version_id.data = category.version_id
        form.name.data = category.name

    return render_template(
        "category/delete.html.jinja",
        title="Delete Category",
        form=form,
        cancel=url_for("category.list"),
    )


@blueprint.route("/list")
@login_required
def list():
    categories = Category.query.order_by(Category.name.asc())

    return render_template(
        "category/list.html.jinja", title="Category", categories=categories
    )

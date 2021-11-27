from traceback import format_exc

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
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
            category = Category(name=form.name.data, filter_=form.filter_.data)
            database.session.add(category)
            database.session.commit()
            flash("The category has been created.")
        except IntegrityError:
            database.session.rollback()
            flash(
                "The category has not been created due to concurrent modification.",
                "error",
            )

        return redirect(url_for("category.list"))

    return render_template(
        "category/create.html.jinja",
        title="Create Category",
        form=form,
        cancel_url=url_for("category.list"),
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
        if form.version_id.data != category.version_id:
            flash(
                "The category has not been updated due to concurrent modification.",
                "error",
            )
            return redirect(url_for("category.list"))

        try:
            category.name = form.name.data
            category.filter_ = form.filter_.data
            database.session.commit()
            flash("The category has been updated.")
        except (IntegrityError, StaleDataError):
            database.session.rollback()
            flash(
                "The category has not been updated due to concurrent modification.",
                "error",
            )

        return redirect(url_for("category.list"))
    elif request.method == "GET":
        form.version_id.data = category.version_id
        form.name.data = category.name
        form.filter_.data = category.filter_

    return render_template(
        "category/update.html.jinja",
        title="Update Category",
        form=form,
        cancel_url=url_for("category.list"),
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
        if form.version_id.data != category.version_id:
            flash(
                "The category has not been deleted due to concurrent modification.",
                "error",
            )
            return redirect(url_for("category.list"))

        try:
            database.session.delete(category)
            database.session.commit()
            flash("The category has been deleted.")
        except IntegrityError:
            # in case of deletion, the foreign key of related items will be set
            # to null, resulting in an integrity error
            database.session.rollback()
            flash(
                "The category has not been deleted because it still contains item(s).",
                "error",
            )
        except StaleDataError:
            database.session.rollback()
            flash(
                "The category has not been deleted due to concurrent modification.",
                "error",
            )

        return redirect(url_for("category.list"))
    elif request.method == "GET":
        form.version_id.data = category.version_id
        form.name.data = category.name
        form.filter_.data = category.filter_

    return render_template(
        "category/delete.html.jinja",
        title="Delete Category",
        form=form,
        cancel_url=url_for("category.list"),
    )


@blueprint.route("/list")
@login_required
def list():
    categories = Category.query.filter(
        or_(
            current_user.filter_ == Category.filter_,
            current_user.filter_ == None,  # noqa: E711
        )
    ).order_by(Category.filter_, Category.name)

    return render_template(
        "category/list.html.jinja", title="Category", categories=categories
    )


@blueprint.route("/get_filters")
@login_required
def get_filters():
    filters = (
        database.session.query(Category.filter_)
        .distinct()
        .order_by(Category.filter_)
        .all()
    )

    return render_template("category/filters.html.jinja", filters=filters)


@blueprint.route("/set_filter", methods=["POST"])
@login_required
def set_filter():
    try:
        data = request.get_json(False, True, False)
        filter_ = data.get("item_id")
        version_id = data.get("version_id")
    except (AttributeError, TypeError, ValueError):
        print(format_exc())
        print(f"data: {data}")
        return jsonify({"status": "missing or invalid data"}), 400

    try:
        if current_user.version_id != version_id:
            raise StaleDataError()

        current_user.filter_ = filter_ if filter_ != "All" else None
        database.session.commit()
        return jsonify({"status": "ok"})
    except (IntegrityError, StaleDataError):
        database.session.rollback()
        flash(
            "The item has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify({"status": "cancel"})

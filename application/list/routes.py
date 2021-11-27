from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.list import blueprint
from application.list.forms import CreateForm, DeleteForm, UpdateForm
from application.models import Category, Item, List, ListItem


@blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        try:
            list_ = List(name=form.name.data)
            database.session.add(list_)
            database.session.commit()
            flash("The list has been created.")
        except IntegrityError:
            database.session.rollback()
            flash(
                "The list has not been created due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.item", list_id=list_.list_id))

    return render_template(
        "list/create.html.jinja",
        title="Create List",
        form=form,
        cancel_url=url_for("list.list"),
    )


@blueprint.route("/update/<int:list_id>", methods=["GET", "POST"])
@login_required
def update(list_id):
    list_ = List.query.get(list_id)
    if list_ is None:
        flash("The list has not been found.", "error")
        return redirect(url_for("list.list"))

    form = UpdateForm(list_.name)
    if form.validate_on_submit():
        if form.version_id.data != list_.version_id:
            flash(
                "The list has not been updated due to concurrent modification.",
                "error",
            )
            return redirect(url_for("list.list"))

        try:
            list_.name = form.name.data
            database.session.commit()
            flash("The list has been updated.")
        except (IntegrityError, StaleDataError):
            database.session.rollback()
            flash(
                "The list has not been updated due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.list"))
    elif request.method == "GET":
        form.version_id.data = list_.version_id
        form.name.data = list_.name

    return render_template(
        "list/update.html.jinja",
        title="Update List",
        form=form,
        cancel_url=url_for("list.list"),
    )


@blueprint.route("/delete/<int:list_id>", methods=["GET", "POST"])
@login_required
def delete(list_id):
    list_ = List.query.get(list_id)
    if list_ is None:
        flash("The list has not been found.", "error")
        return redirect(url_for("list.list"))

    form = DeleteForm()
    if form.validate_on_submit():
        if form.version_id.data != list_.version_id:
            flash(
                "The list has not been deleted due to concurrent modification.",
                "error",
            )
            return redirect(url_for("list.list"))

        try:
            database.session.delete(list_)
            database.session.commit()
            flash("The list has been deleted.")
        except StaleDataError:
            database.session.rollback()
            flash(
                "The list has not been deleted due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.list"))
    elif request.method == "GET":
        form.version_id.data = list_.version_id
        form.name.data = list_.name

    return render_template(
        "list/delete.html.jinja",
        title="Delete List",
        form=form,
        cancel_url=url_for("list.list"),
    )


@blueprint.route("/list")
@login_required
def list():
    if current_user.filter_ is None:
        lists = List.query.order_by(List.name)
    else:
        lists = (
            database.session.query(List)
            .join(ListItem)
            .join(Item)
            .join(Category)
            .filter(Category.filter_ == current_user.filter_)
            .order_by(List.name)
            .all()
        )

    return render_template("list/list.html.jinja", title="List", lists=lists)

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, literal_column, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.list import blueprint
from application.list.forms import CreateForm, DeleteForm, UpdateForm
from application.models import Category, Item, List


@blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        try:
            list_ = List(
                name=form.name.data,
                created_by=current_user.user_id,
                private=form.private.data,
            )
            database.session.add(list_)
            database.session.commit()
            flash("The list has been created.")
        except IntegrityError:
            database.session.rollback()
            flash(
                "The list has not been created due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.read"))

    return render_template(
        "list/create.html.jinja",
        title="Create List",
        form=form,
        cancel_url=url_for("list.read"),
    )


@blueprint.route("/update/<int:list_id>", methods=["GET", "POST"])
@login_required
def update(list_id):
    list_ = List.query.get(list_id)
    if list_ is None or not current_user.has_access(list_):
        flash("The list has not been found.", "error")
        return redirect(url_for("list.read"))

    form = UpdateForm(list_.name)
    if form.validate_on_submit():
        try:
            if list_.version_id != form.version_id.data:
                raise StaleDataError()

            list_.name = form.name.data
            list_.private = form.private.data
            database.session.commit()
            flash("The list has been updated.")
        except (IntegrityError, StaleDataError):
            database.session.rollback()
            flash(
                "The list has not been updated due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.read"))
    elif request.method == "GET":
        form.name.data = list_.name
        form.private.data = list_.private
        form.version_id.data = list_.version_id

    return render_template(
        "list/update.html.jinja",
        title="Update List",
        form=form,
        cancel_url=url_for("list.read"),
    )


@blueprint.route("/delete/<int:list_id>", methods=["GET", "POST"])
@login_required
def delete(list_id):
    list_ = List.query.get(list_id)
    if list_ is None or not current_user.has_access(list_):
        flash("The list has not been found.", "error")
        return redirect(url_for("list.read"))

    form = DeleteForm()
    if form.validate_on_submit():
        try:
            if list_.version_id != form.version_id.data:
                raise StaleDataError()

            database.session.query(Item).filter(
                Item.category_id.in_(
                    database.session.query(Category)
                    .filter(Category.list_id == list_id)
                    .with_entities(Category.category_id)
                )
            ).delete(synchronize_session=False)

            database.session.query(Category).filter(Category.list_id == list_id).delete(
                synchronize_session=False
            )

            database.session.query(List).filter(List.list_id == list_id).delete(
                synchronize_session=False
            )

            database.session.commit()
            flash("The list has been deleted.")
        except StaleDataError:
            database.session.rollback()
            flash(
                "The list has not been deleted due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.read"))
    elif request.method == "GET":
        form.name.data = list_.name
        form.private.data = list_.private
        form.version_id.data = list_.version_id

    category_count = (
        database.session.query(func.count(literal_column("*")))
        .filter(Category.list_id == list_id)
        .scalar()
    )

    item_count = (
        database.session.query(func.count(literal_column("*")))
        .select_from(Item)
        .join(Category)
        .filter(Category.list_id == list_id)
        .scalar()
    )

    return render_template(
        "list/delete.html.jinja",
        title="Delete List",
        form=form,
        category_count=category_count,
        item_count=item_count,
        cancel_url=url_for("list.read"),
    )


@blueprint.route("/read")
@login_required
def read():
    lists = List.query.filter(
        or_(
            List.private == False,  # noqa: E712
            List.created_by == current_user.user_id,
        )
    ).order_by(List.name)

    return render_template("list/read.html.jinja", title="List", lists=lists)

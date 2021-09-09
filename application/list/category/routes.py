from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.list import blueprint
from application.models import Category, List, ListCategory


@blueprint.route("/category/<int:list_id>")
@login_required
def category(list_id):
    list_ = List.query.get(list_id)
    if list_ is None:
        return redirect(url_for("list.list"))

    categories = (
        database.session.query(Category, ListCategory)
        .outerjoin(
            ListCategory,
            and_(
                ListCategory.category_id == Category.category_id,
                ListCategory.list_id == list_id,
            ),
        )
        .order_by(Category.name)
        .all()
    )

    return render_template(
        "list/category/category.html.jinja",
        title="Categories in List",
        list=list_,
        categories=categories,
        cancel=url_for("list.list"),
    )


@blueprint.route("/category/switch_selection", methods=["POST"])
@login_required
def category_switch_selection():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        category_id = int(data.get("category_id"))
        version_id = data.get("version_id")
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    try:
        list_category = ListCategory.query.get((list_id, category_id))
        if list_category is None:
            if version_id != "none":
                raise StaleDataError()

            list_category = ListCategory(list_id=list_id, category_id=category_id)
            database.session.add(list_category)
        else:
            if version_id != list_category.version_id:
                raise StaleDataError()

            database.session.delete(list_category)

        database.session.commit()
        return jsonify(
            {
                "status": "ok",
                "selected": "true" if inspect(list_category).persistent else "false",
                "version": list_category.version_id,
            }
        )
    except (IntegrityError, StaleDataError):
        database.session.rollback()
        flash(
            "The category has not been updated due to concurrent modification.",
            "error",
        )
        return jsonify({"status": "cancel", "url": url_for("list.list")})

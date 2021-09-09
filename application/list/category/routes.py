from flask import jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_

from application import database
from application.list import blueprint
from application.models import Category, List, list_category


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
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    list_ = List.query.get(list_id)
    category = Category.query.get(category_id)

    if list_ is None or category is None:
        return jsonify({"status": "invalid data"}), 400

    list_.categories.append(category)
    database.session.add(list_)
    database.session.commit()

    return jsonify({"status": "ok"})


@blueprint.route("/category/uncheck", methods=["POST"])
@login_required
def category_uncheck():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        category_id = int(data.get("category_id"))
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    list_ = List.query.get(list_id)
    category = Category.query.get(category_id)

    if list_ is None or category is None:
        return jsonify({"status": "invalid data"}), 400

    list_.categories.remove(category)
    database.session.commit()

    return jsonify({"status": "ok"})


@blueprint.route("/category/get")
@login_required
def category_get():
    try:
        list_id = int(request.args.get("list_id"))
        category_id = int(request.args.get("category_id"))
    except (TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    if (
        Category.query.filter(Category.lists.any(list_id=list_id))
        .filter_by(category_id=category_id)
        .first()
    ):
        return jsonify({"status": "checked"})
    else:
        return jsonify({"status": "unchecked"})

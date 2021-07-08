from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from application import database
from application.list import blueprint
from application.list.forms import CreateForm, DeleteForm, UpdateForm
from application.models import Category, Item, List, list_category, list_item


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
                "The list has not been created " + "due to concurrent modification.",
                "error",
            )

        return redirect(url_for("list.list"))

    return render_template(
        "list/create.html.jinja",
        title="Create List",
        form=form,
        cancel=url_for("list.list"),
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
        if form.version_id.data != str(list_.version_id):
            flash(
                "The list has not been updated " + "due to concurrent modification.",
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
                "The list has not been updated " + "due to concurrent modification.",
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
        cancel=url_for("list.list"),
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
        if form.version_id.data != str(list_.version_id):
            flash(
                "The list has not been deleted " + "due to concurrent modification.",
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
                "The list has not been deleted " + "due to concurrent modification.",
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
        cancel=url_for("list.list"),
    )


@blueprint.route("/list")
@login_required
def list():
    lists = List.query.order_by(List.name.asc())

    return render_template("list/list.html.jinja", title="List", lists=lists)


# manage categories in list


@blueprint.route("/category/<int:list_id>")
@login_required
def category(list_id):
    lst = List.query.get(list_id)
    if lst is None:
        return redirect(url_for("list.list"))

    categories = (
        database.session.query(Category, list_category)
        .outerjoin(
            list_category,
            and_(
                list_category.c.category_id == Category.category_id,
                list_category.c.list_id == list_id,
            ),
        )
        .order_by(Category.name)
        .all()
    )

    return render_template(
        "list/category/category.html.jinja",
        title="Categories in List",
        list=lst,
        categories=categories,
        cancel=url_for("list.list"),
    )


@blueprint.route("/category/check", methods=["POST"])
@login_required
def category_check():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        category_id = int(data.get("category_id"))
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    lst = List.query.get(list_id)
    category = Category.query.get(category_id)

    if lst is None or category is None:
        return jsonify({"status": "invalid data"}), 400

    lst.categories.append(category)
    database.session.add(lst)
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

    lst = List.query.get(list_id)
    category = Category.query.get(category_id)

    if lst is None or category is None:
        return jsonify({"status": "invalid data"}), 400

    lst.categories.remove(category)
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


# manage items in list


def warn_unchecked_categories(list_id):
    # checked categories in the list
    checked_categories = database.session.query(Category.category_id).join(
        list_category,
        and_(
            list_category.c.category_id == Category.category_id,
            list_category.c.list_id == list_id,
        ),
    )

    # for the checked items in the list, find the unchecked categories
    unchecked_categories = (
        database.session.query(Category)
        .join(Item)
        .join(
            list_item,
            and_(list_item.c.item_id == Item.item_id, list_item.c.list_id == list_id),
        )
        .filter(Category.category_id.notin_(checked_categories))
        .order_by(Category.name)
    )

    # warn about unchecked categories for checked items
    for category in unchecked_categories:
        flash(
            "Some items are not visible. "
            + f"The category '{category.name}' should be selected.",
            "warning",
        )


@blueprint.route("/item/<int:list_id>")
@login_required
def item(list_id):
    lst = List.query.get(list_id)
    if lst is None:
        return redirect(url_for("list.list"))

    warn_unchecked_categories(list_id)

    items_categories = (
        database.session.query(Item, Category, list_item)
        .join(Category)
        .join(
            list_category,
            and_(
                list_category.c.category_id == Category.category_id,
                list_category.c.list_id == list_id,
            ),
        )
        .outerjoin(
            list_item,
            and_(list_item.c.item_id == Item.item_id, list_item.c.list_id == list_id),
        )
        .order_by(Category.name, Item.name)
        .all()
    )

    return render_template(
        "list/item/item.html.jinja",
        title="Items in List",
        list=lst,
        items_categories=items_categories,
        cancel=url_for("list.list"),
    )


@blueprint.route("/item/check", methods=["POST"])
@login_required
def item_check():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    lst = List.query.get(list_id)
    item = Item.query.get(item_id)

    if lst is None or item is None:
        return jsonify({"status": "invalid data"}), 400

    lst.items.append(item)
    database.session.add(lst)
    database.session.commit()

    return jsonify({"status": "ok"})


@blueprint.route("/item/uncheck", methods=["POST"])
@login_required
def item_uncheck():
    try:
        data = request.get_json(False, True, False)
        list_id = int(data.get("list_id"))
        item_id = int(data.get("item_id"))
    except (AttributeError, TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    lst = List.query.get(list_id)
    item = Item.query.get(item_id)

    if lst is None or item is None:
        return jsonify({"status": "invalid data"}), 400

    lst.items.remove(item)
    database.session.commit()

    return jsonify({"status": "ok"})


@blueprint.route("/item/get")
@login_required
def item_get():
    try:
        list_id = int(request.args.get("list_id"))
        item_id = int(request.args.get("item_id"))
    except (TypeError, ValueError):
        return jsonify({"status": "missing or invalid data"}), 400

    if (
        Item.query.filter(Item.lists.any(list_id=list_id))
        .filter_by(item_id=item_id)
        .first()
    ):
        return jsonify({"status": "checked"})
    else:
        return jsonify({"status": "unchecked"})

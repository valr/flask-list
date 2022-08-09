from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from application import database
from application.list import blueprint
from application.models import Category, Item, List


@blueprint.route("/detail/<int:list_id>")
@login_required
def detail(list_id):
    list_ = List.query.get(list_id)
    if list_ is None or not current_user.has_access(list_):
        flash("The list has not been found.", "error")
        return redirect(url_for("list.read"))

    categories_items = (
        database.session.query(Category, Item)
        .outerjoin(Item)
        .join(List)
        .filter(List.list_id == list_id)
        .order_by(Category.name, Item.name)
        .all()
    )

    return render_template(
        "list/detail/read.html.jinja",
        title="Details of List",
        list=list_,
        categories_items=categories_items,
        cancel_url=url_for("list.read"),
    )

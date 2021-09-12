from flask import redirect, render_template, url_for
from flask_login import login_required
from sqlalchemy import and_

from application import database
from application.list import blueprint
from application.models import Category, Item, List, ListItem


@blueprint.route("/use/<int:list_id>")
@login_required
def use(list_id):
    list_ = List.query.get(list_id)
    if list_ is None:
        return redirect(url_for("list.list"))

    items_categories = (
        database.session.query(Item, Category, ListItem)
        .join(Category)
        .join(
            ListItem,
            and_(ListItem.item_id == Item.item_id, ListItem.list_id == list_id),
        )
        .order_by(Category.name, Item.name)
        .all()
    )

    return render_template(
        "list/use/list.html.jinja",
        title=f"List - {list_.name}",
        list=list_,
        items_categories=items_categories,
        cancel=url_for("list.list"),
    )

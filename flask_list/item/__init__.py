from flask import Blueprint

blueprint = Blueprint("item", __name__)

from flask_list.item import routes  # noqa: E402, F401

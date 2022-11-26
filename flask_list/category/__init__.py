from flask import Blueprint

blueprint = Blueprint("category", __name__)

from flask_list.category import routes  # noqa: E402, F401

from flask import Blueprint

blueprint = Blueprint("item", __name__)

from application.item import routes  # noqa: E402, F401

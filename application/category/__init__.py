from flask import Blueprint

blueprint = Blueprint("category", __name__)

from application.category import routes  # noqa: E402, F401

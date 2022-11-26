from flask import Blueprint

blueprint = Blueprint("auth", __name__)

from flask_list.auth import routes  # noqa: E402, F401

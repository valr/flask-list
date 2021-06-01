from flask import Blueprint

blueprint = Blueprint("list", __name__)

from application.list import routes  # noqa: E402, F401

from flask import Blueprint

blueprint = Blueprint("auth", __name__)

from application.auth import routes  # noqa: E402, F401

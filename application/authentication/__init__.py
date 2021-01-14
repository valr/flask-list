from flask import Blueprint

blueprint = Blueprint('authentication', __name__)

from application.authentication import routes  # noqa: E402, F401

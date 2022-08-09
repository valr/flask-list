from flask import Blueprint

blueprint = Blueprint("list", __name__)

from application.list import routes  # noqa: E402, F401
from application.list.detail import routes  # noqa: E402, F401, F811

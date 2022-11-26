from flask import Blueprint

blueprint = Blueprint("list", __name__)

from flask_list.list import routes  # noqa: E402, F401
from flask_list.list.detail import routes  # noqa: E402, F401, F811

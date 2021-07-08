from flask import Blueprint

blueprint = Blueprint("list", __name__)

from application.list import routes  # noqa: E402, F401
from application.list.category import routes  # noqa: E402, F401, F811
from application.list.item import routes  # noqa: E402, F401, F811
from application.list.list import routes  # noqa: E402, F401, F811

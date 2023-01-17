from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_paranoid import Paranoid
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from jinja2 import select_autoescape
from sqlalchemy import event
from sqlalchemy.engine import Engine

database = SQLAlchemy()
migrate = Migrate()

csrf = CSRFProtect()
login = LoginManager()
paranoid = Paranoid()
talisman = Talisman()

bootstrap = Bootstrap5()
cache = Cache()
mail = Mail()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_application(instance_path, config_file="flask-list.conf"):
    if instance_path:
        application = Flask(
            __name__, instance_relative_config=True, instance_path=instance_path
        )
    else:
        application = Flask(__name__, instance_relative_config=True)

    application.config.from_pyfile(config_file)

    # set remember cookie attributes
    application.config["REMEMBER_COOKIE_SECURE"] = True
    application.config["REMEMBER_COOKIE_HTTPONLY"] = True
    application.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"

    application.jinja_env.trim_blocks = True
    application.jinja_env.lstrip_blocks = True
    application.jinja_env.autoescape = select_autoescape(
        ["html", "htm", "xml", "jinja"]  # adding jinja to default
    )

    database.init_app(application)
    migrate.init_app(application, database)

    csrf.init_app(application)
    login.init_app(application)
    login.session_protection = None  # using paranoid
    paranoid.init_app(application)
    paranoid.redirect_view = "auth.login"
    talisman.init_app(
        application,
        content_security_policy={
            "base-uri": "'none'",
            "object-src": "'none'",
            "default-src": "'self'",
            "img-src": ["'self'", "data:"],
            "script-src": ["'unsafe-inline'", "'strict-dynamic'", "https:", "http:"],
            "style-src": ["'self'", "fonts.googleapis.com"],
            "font-src": ["'self'", "fonts.gstatic.com"],
        },
        content_security_policy_nonce_in=["script-src", "style-src"],
    )

    bootstrap.init_app(application)
    cache.init_app(application)
    cache.cache._client.behaviors.update({"tcp_nodelay": True, "tcp_keepalive": True})
    mail.init_app(application)

    from flask_list.auth import blueprint as auth_blueprint

    application.register_blueprint(auth_blueprint, url_prefix="/auth")

    from flask_list.category import blueprint as category_blueprint

    application.register_blueprint(category_blueprint, url_prefix="/category")

    from flask_list.item import blueprint as item_blueprint

    application.register_blueprint(item_blueprint, url_prefix="/item")

    from flask_list.list import blueprint as list_blueprint

    application.register_blueprint(list_blueprint, url_prefix="/list")

    return application


from flask_list import models  # noqa: E402, F401

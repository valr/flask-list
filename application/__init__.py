from flask import Flask
from flask_bootstrap import Bootstrap4
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

bootstrap = Bootstrap4()
mail = Mail()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_application(instance_path):
    if instance_path:
        application = Flask(
            __name__, instance_relative_config=True, instance_path=instance_path
        )
    else:
        application = Flask(__name__, instance_relative_config=True)

    application.config.from_pyfile("flask-list.conf")

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
        strict_transport_security=False,  # setup in web server
        content_security_policy={
            "font-src": ["'self'", "*.gstatic.com"],
            "style-src": ["'self'", "*.gstatic.com", "fonts.googleapis.com"],
            "script-src": "'self'",
            "default-src": "'self'",
        },
        content_security_policy_nonce_in=["script-src", "style-src"],
    )

    bootstrap.init_app(application)
    mail.init_app(application)

    from application.auth import blueprint as auth_blueprint

    application.register_blueprint(auth_blueprint, url_prefix="/auth")

    from application.category import blueprint as category_blueprint

    application.register_blueprint(category_blueprint, url_prefix="/category")

    from application.item import blueprint as item_blueprint

    application.register_blueprint(item_blueprint, url_prefix="/item")

    from application.list import blueprint as list_blueprint

    application.register_blueprint(list_blueprint, url_prefix="/list")

    return application


from application import models  # noqa: E402, F401

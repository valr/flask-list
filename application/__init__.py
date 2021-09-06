from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_paranoid import Paranoid
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

database = SQLAlchemy()
migrate = Migrate()

csrf = CSRFProtect()
login = LoginManager()
paranoid = Paranoid()
talisman = Talisman()

bootstrap = Bootstrap()
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

    # set session cookie attribute not covered yet by flask-talisman (PR opened)
    # https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options
    # https://github.com/GoogleCloudPlatform/flask-talisman/pull/51
    application.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # set remember cookie attributes
    application.config["REMEMBER_COOKIE_SECURE"] = True
    application.config["REMEMBER_COOKIE_HTTPONLY"] = True
    application.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"

    application.jinja_env.trim_blocks = True
    application.jinja_env.lstrip_blocks = True

    database.init_app(application)
    migrate.init_app(application, database)

    csrf.init_app(application)
    login.init_app(application)
    login.session_protection = None  # using paranoid
    paranoid.init_app(application)
    paranoid.redirect_view = "authentication.login"
    talisman.init_app(
        application,
        strict_transport_security=False,  # setup in webserver
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

    from application.authentication import \
        blueprint as authentication_blueprint

    application.register_blueprint(
        authentication_blueprint, url_prefix="/authentication"
    )

    from application.category import blueprint as category_blueprint

    application.register_blueprint(category_blueprint, url_prefix="/category")

    from application.item import blueprint as item_blueprint

    application.register_blueprint(item_blueprint, url_prefix="/item")

    from application.list import blueprint as list_blueprint

    application.register_blueprint(list_blueprint, url_prefix="/list")

    return application


from application import models  # noqa: E402, F401

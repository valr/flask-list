import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    REGISTRATION = os.environ.get('REGISTRATION_ALLOWED') or 'True'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rgUbxlUn6sGl0DJ6nrqb'

    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database', 'application.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_FROM = os.environ.get('MAIL_FROM') or 'user@local.host'
    MAIL_TO = \
        [var for var in (os.environ.get('MAIL_TO') or '').split(' ') if var]

    BOOTSTRAP_BOOTSWATCH_THEME = os.environ.get('BOOTSTRAP_THEME')
    BOOTSTRAP_SERVE_LOCAL = True

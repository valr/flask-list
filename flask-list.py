import os

from flask import redirect, render_template, url_for

from application import create_application, database
from application.models import Category, Item, List, User

application = create_application(os.environ.get('INSTANCE_PATH'))


@application.route('/')
@application.route('/index')
def index():
    return redirect(url_for('list.list'))


@application.route('/favicon.ico')
def favicon():
    return application.send_static_file('favicon.ico')


@application.errorhandler(404)
def not_found(error):
    return render_template('error/404.html'), 404


@application.errorhandler(500)
def internal_server_error(error):
    database.session.rollback()
    return render_template('error/500.html'), 500


# flask shell

@application.shell_context_processor
def make_shell_context():
    return {
        'application': application,
        'database': database,
        'Category': Category,
        'Item': Item,
        'List': List,
        'User': User
    }

from datetime import datetime, timedelta

from application import database, login
from application.authentication import blueprint
from application.authentication.emails import (send_register_email,
                                               send_reset_password_email)
from application.authentication.forms import (LoginForm, ProfileForm,
                                              RegisterForm,
                                              ResetPasswordConfirmationForm,
                                              ResetPasswordForm)
from application.models import User
from flask import (current_app, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError
from werkzeug.routing import BuildError


@login.unauthorized_handler
def unauthorized_user():
    return redirect(url_for('authentication.login', next=request.endpoint))


@login.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except ValueError:
        return None


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data, active=False)
            user.set_password(form.password.data)
            database.session.add(user)
            database.session.commit()
        except IntegrityError:
            database.session.rollback()
            flash('The user has not been registered ' +
                  'due to concurrent modification.', 'error')
        else:
            send_register_email(user)
            flash('An email has been sent to confirm your registration.')

        return redirect(url_for('authentication.login'))

    return render_template(
        'authentication/register.html', title='Register', form=form,
        cancel=url_for('index'))


@blueprint.route('/register_confirmation/<token>')
def register_confirmation(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_token(token, 'register')
    if not user:
        flash('The registration token is invalid or has expired.', 'error')
        return redirect(url_for('index'))

    user.active = True
    database.session.commit()

    flash('The registration is successful!')
    return redirect(url_for('authentication.login'))


# cli command: flask authentication cleaning
@blueprint.cli.command('cleaning')
def register_cleaning():
    expired_on = datetime.utcnow() - timedelta(hours=1)
    User.query.filter(User.active == False,
                      User.updated_on < expired_on).delete()
    database.session.commit()
    print('The inactive users have been cleaned.')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('The email or password is invalid.', 'error')
            return redirect(url_for('authentication.login'))

        if not user.active:
            flash('The user is inactive.', 'warning')
            return redirect(url_for('authentication.login'))

        login_user(user, remember=form.remember_me.data)

        try:
            return redirect(url_for(request.args.get('next', 'index')))
        except BuildError:
            return redirect(url_for('index'))

    return render_template(
        'authentication/login.html', title='Sign In', form=form,
        registration_allowed=current_app.config['REGISTRATION_ALLOWED'])


@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.version_id.data != str(current_user.version_id):
            flash('The profile has not been saved ' +
                  'due to concurrent modification.', 'error')
            return redirect(url_for('index'))

        try:
            # check if all password fields are filled-in
            # check if the new password and confirmed new password are the same
            if form.password_curr.data and \
               form.password.data and form.password_conf.data and \
               form.password.data == form.password_conf.data:
                # check if the current password is valid
                if current_user.verify_password(form.password_curr.data):
                    current_user.set_password(form.password.data)
                    database.session.commit()
                    flash('The password has been changed.')
                else:
                    flash('The current password is invalid.', 'error')

            # current_user.xxx = form.yyy.data
            # database.session.commit()
            # flash('The profile has been saved.')
        except StaleDataError:
            database.session.rollback()
            flash('The profile has not been saved ' +
                  'due to concurrent modification.', 'error')

        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.version_id.data = current_user.version_id
        form.email.data = current_user.email
        # form.yyy.data = current_user.xxx

    return render_template(
        'authentication/profile.html', title='Profile', form=form,
        cancel=url_for('index'))


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_password_email(user)

        # always display the message even if no email has been sent
        flash('An email has been sent to reset your password.')
        return redirect(url_for('authentication.login'))

    return render_template(
        'authentication/reset_password.html', title='Reset Password',
        form=form, cancel=url_for('index'))


@blueprint.route('/reset_password_confirmation/<token>', methods=['GET', 'POST'])
def reset_password_confirmation(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_token(token, 'reset_password')
    if not user:
        flash('The reset password token is invalid or has expired.', 'error')
        return redirect(url_for('index'))

    form = ResetPasswordConfirmationForm()
    if form.validate_on_submit():
        # check if all password fields are filled-in
        # check if the new password and confirmed new password are the same
        if form.password.data and form.password_conf.data and \
           form.password.data == form.password_conf.data:
            user.set_password(form.password.data)
            database.session.commit()
            flash('Your password has been reset.')

        return redirect(url_for('authentication.login'))

    return render_template(
        'authentication/reset_password_confirmation.html',
        title='Reset Password', form=form, cancel=url_for('index'))

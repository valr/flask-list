from datetime import datetime, timedelta
from uuid import uuid4

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.routing import BuildError

from flask_list import cache, database, login
from flask_list.auth import blueprint
from flask_list.auth.emails import (
    send_invite_email,
    send_register_email,
    send_reset_password_email,
)
from flask_list.auth.forms import (
    ChangePasswordForm,
    InviteForm,
    LoginForm,
    RegisterForm,
    ResetPasswordConfirmationForm,
    ResetPasswordForm,
)
from flask_list.models import User


@login.unauthorized_handler
def unauthorized_user():
    return redirect(url_for("auth.login", next=request.endpoint))


@login.user_loader
def load_user(user_id):
    key = f"user_{user_id}"
    user = cache.get(key)
    if user is None:
        user = User.query.get(int(user_id))
        cache.set(key, user)

    return user


# cli command: flask auth cleaning
@blueprint.cli.command("cleaning")
def register_cleaning():
    expired_on = datetime.utcnow() - timedelta(hours=1)
    User.query.filter(
        User.active == False, User.updated_on < expired_on  # noqa: E712
    ).delete()
    database.session.commit()


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated or not current_app.config["REGISTRATION_ALLOWED"]:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data, active=False)
            user.set_password(form.password.data)
            database.session.add(user)
            database.session.commit()
        except IntegrityError:
            database.session.rollback()
            flash(
                "The user has not been registered due to concurrent modification.",
                "error",
            )
        else:
            send_register_email(user)
            flash("An email has been sent to confirm your registration.")

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html.jinja",
        title="Register",
        form=form,
        cancel_url=url_for("index"),
    )


@blueprint.route("/register_confirmation/<token>")
def register_confirmation(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    user = User.verify_token(token, "register")
    if not user:
        flash("The registration token is invalid or has expired.", "error")
        return redirect(url_for("index"))

    user.active = True
    database.session.commit()

    flash("The registration is successful!")
    return redirect(url_for("auth.login"))


@blueprint.route("/invite", methods=["GET", "POST"])
@login_required
def invite():
    form = InviteForm()
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data, active=True)
            user.set_password(uuid4().hex)
            database.session.add(user)
            database.session.commit()
        except IntegrityError:
            database.session.rollback()
            flash(
                "The user has not been invited due to concurrent modification.",
                "error",
            )
        else:
            send_invite_email(user)
            flash("An email has been sent to invite the user.")

        return redirect(url_for("index"))

    return render_template(
        "auth/invite.html.jinja",
        title="Invite User",
        form=form,
        cancel_url=url_for("index"),
    )


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash("The email or password is invalid.", "error")
            return redirect(url_for("auth.login"))

        if not user.active:
            flash("The user is inactive.", "warning")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)

        try:
            return redirect(url_for(request.args.get("next", "index")))
        except BuildError:
            return redirect(url_for("index"))

    return render_template(
        "auth/login.html.jinja",
        title="Sign In",
        form=form,
        registration_allowed=current_app.config["REGISTRATION_ALLOWED"],
    )


@blueprint.route("/logout")
@login_required
def logout():
    cache.delete(f"user_{current_user.user_id}")
    logout_user()
    return redirect(url_for("index"))


@blueprint.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if form.version_id.data != current_user.version_id:
            flash(
                "The password has not been saved due to concurrent modification.",
                "error",
            )
            return redirect(url_for("index"))

        # check if all password fields are filled-in
        # check if the new password and confirmed new password are the same
        if (
            form.password_curr.data
            and form.password.data
            and form.password_conf.data
            and form.password.data == form.password_conf.data
        ):
            # check if the current password is valid
            if current_user.verify_password(form.password_curr.data):
                user = User.query.get(current_user.user_id)
                user.set_password(form.password.data)
                database.session.commit()
                cache.delete(f"user_{current_user.user_id}")
                flash("The password has been changed.")
            else:
                flash("The current password is invalid.", "error")

        return redirect(url_for("index"))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.version_id.data = current_user.version_id

    return render_template(
        "auth/change_password.html.jinja",
        title="Change Password",
        form=form,
        cancel_url=url_for("index"),
    )


@blueprint.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_password_email(user)

        # always display the message even if no email has been sent
        flash("An email has been sent to reset your password.")
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password.html.jinja",
        title="Reset Password",
        form=form,
        cancel_url=url_for("index"),
    )


@blueprint.route("/reset_password_confirmation/<token>", methods=["GET", "POST"])
def reset_password_confirmation(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    user = User.verify_token(token, "reset_password")
    if not user:
        flash("The reset password token is invalid or has expired.", "error")
        return redirect(url_for("index"))

    form = ResetPasswordConfirmationForm()
    if form.validate_on_submit():
        # check if all password fields are filled-in
        # check if the new password and confirmed new password are the same
        if (
            form.password.data
            and form.password_conf.data
            and form.password.data == form.password_conf.data
        ):
            user.set_password(form.password.data)
            database.session.commit()
            flash("Your password has been reset.")

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_confirmation.html.jinja",
        title="Reset Password",
        form=form,
        cancel_url=url_for("index"),
    )

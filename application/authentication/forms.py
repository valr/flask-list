from application.models import User
from flask_wtf import FlaskForm
from wtforms import (BooleanField, HiddenField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)


class RegisterForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(max=256), Email()],
        render_kw={'autofocus': True})

    password = PasswordField('Password', validators=[DataRequired()])
    password_conf = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Field is not equal to Password.')])

    submit = SubmitField('Register')
    cancel = SubmitField('Cancel', render_kw={'type': 'button'})

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email address is already registered.')


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(max=256), Email()],
        render_kw={'autofocus': True})

    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ProfileForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(max=256), Email()],
        render_kw={'readonly': True})

    password_curr = PasswordField(
        'Current Password',
        render_kw={'autofocus': True})

    password = PasswordField('New Password')
    password_conf = PasswordField(
        'Confirm New Password',
        validators=[
            EqualTo('password',
                    message='Field is not equal to New Password.')])

    version_id = HiddenField('Version', render_kw={'readonly': True})
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel', render_kw={'type': 'button'})


class ResetPasswordForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(max=256), Email()],
        render_kw={'autofocus': True})

    submit = SubmitField('Reset Password')
    cancel = SubmitField('Cancel', render_kw={'type': 'button'})


class ResetPasswordConfirmationForm(FlaskForm):
    password = PasswordField(
        'New Password',
        validators=[DataRequired()],
        render_kw={'autofocus': True})

    password_conf = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(),
            EqualTo('password',
                    message='Field is not equal to New Password.')])

    submit = SubmitField('Reset Password')
    cancel = SubmitField('Cancel', render_kw={'type': 'button'})

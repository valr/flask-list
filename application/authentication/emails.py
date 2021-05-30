from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from application import mail


def send_async_email(application, message):
    with application.app_context():
        mail.send(message)


def send_email(subject, sender, recipients, text_body, html_body):
    message = Message(subject, sender=sender, recipients=recipients)
    message.body = text_body
    message.html = html_body

    Thread(target=send_async_email,
           args=(current_app._get_current_object(), message)).start()


def send_register_email(user):
    token = user.get_token('register')

    send_email(
        'Confirm Your Registration',
        sender=current_app.config['MAIL_FROM'],
        recipients=[user.email],
        text_body=render_template(
            'authentication/email/register.txt', user=user, token=token),
        html_body=render_template(
            'authentication/email/register.html', user=user, token=token))


def send_reset_password_email(user):
    token = user.get_token('reset_password')

    send_email(
        'Reset Your Password',
        sender=current_app.config['MAIL_FROM'],
        recipients=[user.email],
        text_body=render_template(
            'authentication/email/reset_password.txt', user=user, token=token),
        html_body=render_template(
            'authentication/email/reset_password.html', user=user, token=token))

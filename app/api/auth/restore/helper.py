from flask import abort
from flask_mail import Message

from app import mail
from app.api.helper import response
from app.api.validators import (validate_password,
                                validate_captcha,
                                validate_code,
                                validate_email_and_user_is_not_registered)


def restore_response(email):
    return response(True, 200, message=f"Message with restoration link has been successfully "
                                       f"sent to '{email}'.")


def password_response(email):
    return response(True, 200, message=f"Password for user '{email}' has been successfully set.")


def restore_error_response(errors):
    return response(False, 200, errors=errors)


def validate_restore_request(data):
    errors = {}
    validate_email_and_user_is_not_registered(data.email, errors)
    return errors if errors else None


def validate_password_request(data):
    errors = {}
    validate_code(data.code, errors)
    validate_password(data.password, errors)
    validate_captcha(data.captcha, data.captcha_secret, errors)
    return errors if errors else None


def send_email(recipient, subject, message):
    try:
        msg = Message(subject)
        msg.add_recipient(recipient)
        msg.body = message
        mail.send(msg)
    except Exception as e:
        abort(503, e)

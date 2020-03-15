from flask import abort
from flask_mail import Message

from app import mail
from app.api.auth.register.helper import is_registered
from app.api.helper import response, is_valid_email


def restore_response(email):
    return response(True, 200, message=f"Message with restoration link has been successfully "
                                       f"sent to '{email}'.")


def restore_error_response(errors):
    return response(False, 400, errors=errors)


def validate_restore_request(data):
    errors = {}
    check_email = True

    if not is_valid_email(data.email):
        errors['e_mail'] = 'Wrong email.'
        check_email = False

    if check_email and not is_registered(data.email):
        errors['e_mail'] = f"User with email '{data.email}' is not registered."

    return errors if errors else None


def send_email(recipient, subject, message):
    try:
        msg = Message(subject)
        msg.add_recipient(recipient)
        msg.body = message
        mail.send(msg)
    except Exception as e:
        abort(503, e)

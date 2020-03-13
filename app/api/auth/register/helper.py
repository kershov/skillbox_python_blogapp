import re

from app import app
from app.api.helper import response
from app.models import CaptchaCode, User

EMAIL_PATTERN = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')


def registration_success_response(user):
    return response(True, 200, message=f"User '{user.email}' successfully registered.")


def registration_error_response(errors):
    return response(False, 400, errors=errors)


def validate_registration_request(data):
    errors = {}

    pwd_min_length = app.config['PASSWORD']['min']
    pwd_max_length = app.config['PASSWORD']['max']

    email = data.get('e_mail')
    password = data.get('password')
    captcha = data.get('captcha')
    captcha_secret = data.get('captcha_secret')

    if not re.match(EMAIL_PATTERN, email):
        errors['e_mail'] = 'Wrong email.'

    if is_registered(email):
        errors['e_mail'] = f"User with email '{email}' is already registered."

    if not (pwd_min_length <= len(password) <= pwd_max_length):
        errors['password'] = f'Wrong password. Password has to be from {pwd_min_length} up to {pwd_max_length} chars.'

    if not is_valid_captcha(captcha, captcha_secret):
        errors['captcha'] = 'Wrong captcha.'

    return errors if bool(errors) else None


def is_registered(email):
    return True if User.get_by_email(email) else False


def is_valid_captcha(code, secret):
    captcha = CaptchaCode.find_by_secret_code(secret)
    return captcha is not None and captcha.is_valid_code(code)

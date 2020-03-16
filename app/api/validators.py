import re

from app import app
from app.models import User, CaptchaCode


def is_valid_email(email: str):
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z]+$')
    return re.match(email_pattern, email)


def is_registered(email):
    return True if User.get_by_email(email) else False


def is_valid_password(password: str):
    min_length = app.config['PASSWORD']['min']
    max_length = app.config['PASSWORD']['max']
    return min_length <= len(password) <= max_length


def validate_password(data, errors):
    if not is_valid_password(data.password):
        min_length = app.config['PASSWORD']['min']
        max_length = app.config['PASSWORD']['max']
        errors['password'] = f'Wrong password. Password has to be from {min_length} up to {max_length} chars.'


def is_valid_captcha(code, secret):
    captcha = CaptchaCode.get_by_secret_code(secret)
    return captcha is not None and captcha.is_valid_code(code)


def validate_captcha(data, errors):
    if not is_valid_captcha(data.captcha, data.captcha_secret):
        errors['captcha'] = 'Код с картинки введен неверно.'


def validate_code(data, errors):
    if not data.code or not User.get_by_code(data.code):
        errors['code'] = 'Ссылка для восстановления пароля устарела. ' \
                         '<a href="/login/restore-password">Запросить ссылку снова</a>.'


def validate_email_and_user_is_not_registered(data, errors):
    check_email = True
    email = data.email if 'email' in dir(data) else data.e_mail

    if not is_valid_email(email):
        errors['email'] = 'Неправильный формат адреса.'
        check_email = False

    if check_email and not is_registered(email):
        errors['email'] = f"Пользователь с таким адресом не зарегистрирован."

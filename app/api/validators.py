import re

from app import app
from app.models import User, CaptchaCode


def is_valid_email(email: str):
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z]+$')
    return re.match(email_pattern, email)


def is_registered(email):
    return True if User.get_by_email(email) else False


def is_valid_password(password: str):
    min_length, max_length = app.config['PASSWORD']['min'], app.config['PASSWORD']['max']
    return min_length <= len(password) <= max_length


def validate_username(name, errors):
    min_length, max_length = app.config['USERNAME']['min'], app.config['USERNAME']['max']
    if not (min_length <= len(name) <= max_length):
        errors['name'] = f'Имя должно быть от {min_length} до {max_length} символов.'


def validate_password(password, errors):
    if not is_valid_password(password):
        min_length, max_length = app.config['PASSWORD']['min'], app.config['PASSWORD']['max']
        errors['password'] = f'Пароль должен быть от {min_length} до {max_length} символов.'


def is_valid_captcha(code, secret):
    captcha = CaptchaCode.get_by_secret_code(secret)
    return captcha is not None and captcha.is_valid_code(code)


def validate_captcha(captcha, captcha_secret, errors):
    if not is_valid_captcha(captcha, captcha_secret):
        errors['captcha'] = 'Код с картинки введен неверно.'


def validate_code(code, errors):
    if not code or not User.get_by_code(code):
        errors['code'] = 'Ссылка для восстановления пароля устарела. ' \
                         '<a href="/login/restore-password">Запросить ссылку снова</a>.'


def validate_email_and_user_is_not_registered(email, errors):
    check_email = True

    if not is_valid_email(email):
        errors['email'] = 'Неправильный формат адреса.'
        check_email = False

    if check_email and not is_registered(email):
        errors['email'] = f"Пользователь с таким адресом не зарегистрирован."


def validate_title(title, errors):
    min_length, max_length = app.config['TITLE']['min'], app.config['TITLE']['max']
    if not (min_length <= len(title) <= max_length):
        errors['title'] = f'Заголовок дожен быть от {min_length} до {max_length} символов.'


def validate_text(text, errors):
    min_length, max_length = app.config['TEXT']['min'], app.config['TEXT']['max']
    if not (min_length <= len(text) <= max_length):
        errors['text'] = f'Текст дожен быть от {min_length} до {max_length} символов.'

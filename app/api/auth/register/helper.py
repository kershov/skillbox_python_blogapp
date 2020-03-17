from app.api.helper import response
from app.api.validators import is_valid_email, is_registered, validate_password, validate_captcha


def registration_success_response(user):
    return response(True, 200, message=f"User with email '{user.email}' has been successfully registered.")


def registration_error_response(errors):
    return response(False, 200, errors=errors)


def validate_registration_request(data):
    errors = {}
    check_email = True

    if not is_valid_email(data.e_mail):
        errors['email'] = 'Неправильный формат адреса.'
        check_email = False

    if check_email and is_registered(data.e_mail):
        errors['email'] = f"Пользователь с таким адресом уже зарегистрирован."

    validate_password(data, errors)

    validate_captcha(data, errors)

    return errors if errors else None
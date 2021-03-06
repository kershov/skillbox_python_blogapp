import uuid

from flask import Blueprint, request

from app.api.auth.restore.helper import (
    restore_error_response,
    validate_restore_request,
    restore_response,
    send_email,
    validate_password_request,
    password_response
)
from app.api.helper import check_request, error_response
from app.models import User

api_restore_password = Blueprint('api_restore', __name__)


@api_restore_password.route('/api/auth/restore', methods=['POST'])
def restore():
    mandatory_fields = {'email'}
    data = check_request(request, mandatory_fields)
    errors = validate_restore_request(data)

    if errors:
        return restore_error_response(errors)

    code = str(uuid.uuid4())

    send_email(
        recipient=data.email,
        subject='Ссылка для восстановления пароля',
        message='Для восстановления пароля, пройдите по этой ссылке: '
                f'{request.host_url}login/change-password/{code}'
    )

    user = User.get_by_email(data.email)
    user.code = code
    user.save()

    return restore_response(user.email)


@api_restore_password.route('/api/auth/password', methods=['POST'])
def password():
    mandatory_fields = {'code', 'password', 'captcha', 'captcha_secret'}
    data = check_request(request, mandatory_fields)
    errors = validate_password_request(data)

    if errors:
        return restore_error_response(errors)

    user = User.get_by_code(data.code)
    user.password = data.password
    user.code = None
    user.save()

    return password_response(user.email)


@api_restore_password.errorhandler(400)
def handle_400_error(e):
    return error_response(e)


@api_restore_password.errorhandler(503)
def handle_503_error(e):
    return error_response(e)

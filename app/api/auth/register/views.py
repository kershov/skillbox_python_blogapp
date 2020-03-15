from flask import Blueprint, request

from app.api.auth.register.helper import (
    validate_registration_request,
    registration_error_response,
    registration_success_response
)
from app.api.helper import response, check_request
from app.models import User

api_register = Blueprint('api_register', __name__)


@api_register.route('/api/auth/register', methods=['POST'])
def register_user():
    mandatory_fields = {'e_mail', 'password', 'captcha', 'captcha_secret'}

    data = check_request(request, mandatory_fields)

    errors = validate_registration_request(data)

    if errors:
        return registration_error_response(errors)

    email = data.get('e_mail')
    password = data.get('password')

    user = User.create_user(email, password)

    return registration_success_response(user)


@api_register.errorhandler(400)
def handle_400_error(e):
    return response(False, e.code, message=f"{e.name}: {e.description}")

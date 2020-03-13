from flask import Blueprint, request, abort

from app.api.auth.register.helper import validate_registration_request, registration_error_response, \
    registration_success_response
from app.api.helper import response
from app.models import User

api_register = Blueprint('api_register', __name__)


@api_register.route('/api/auth/register', methods=['POST'])
def register_user():
    if request.content_type != 'application/json':
        abort(400, "Content-type must be 'application/json'.")

    data = request.data

    if not data:
        abort(400, 'Request has no body.')

    data = request.get_json()

    if {'e_mail', 'password', 'captcha', 'captcha_secret'} != set(data):
        abort(400, "Wrong body. Either one or more mandatory parameters are wrong, don't exist or misspelled. "
                   "Mandatory parameters are: 'e_mail', 'password', 'captcha', 'captcha_secret'.")

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

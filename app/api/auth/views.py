from flask import Blueprint, request, session, g

from app.api.auth.helper import (login_error_response,
                                 validate_login_request,
                                 login_response,
                                 logout_response,
                                 unauthorized_user_response,
                                 authorized_user_response)
from app.api.helper import check_request

api_auth = Blueprint('api_auth', __name__)


@api_auth.route('/api/auth/login', methods=['POST'])
def login():
    mandatory_fields = {'e_mail', 'password'}
    data = check_request(request, mandatory_fields)
    errors, user = validate_login_request(data)

    if errors:
        return login_error_response(errors=errors)

    if 'user' not in session:
        session.permanent = True
        session['user'] = dict(id=user.id, email=user.email, is_moderator=user.is_moderator)

    return login_response(user)


@api_auth.route('/api/auth/check', methods=['GET'])
def check():
    return authorized_user_response(g.user.get('id')) if g.user else unauthorized_user_response()


@api_auth.route('/api/auth/logout', methods=['GET'])
def logout():
    user = session.pop('user', None)
    return logout_response(user.get('email') if user else None)


@api_auth.errorhandler(400)
def handle_400_error(e):
    return login_error_response(message=e.description)

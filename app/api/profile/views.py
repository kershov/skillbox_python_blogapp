from flask import Blueprint, request, abort

from app.api.auth.helper import auth_required
from app.api.helper import error_response
from app.api.profile.helper import (
    validate_profile_fields,
    profile_error_response,
    update_profile,
    get_form_data,
    get_json_data
)

api_profile = Blueprint('api_profile', __name__)


@api_profile.route('/api/profile/my', methods=['POST'])
@auth_required
def profile(user):
    if (not request.form) == (not request.data):            # similar to: not (a ^ b)
        abort(400, "You're not allowed to pass empty request or both form-data and json.")

    data = None

    if request.form:
        data = get_form_data(request)
    elif request.data:
        data = get_json_data(request)

    data.own_email = (data.email == user.email)

    errors = validate_profile_fields(data)

    if errors:
        return profile_error_response(errors)

    return update_profile(user.id, data)


@api_profile.errorhandler(400)
def handle_400_error(e):
    return error_response(e)


@api_profile.errorhandler(500)
def handle_500_error(e):
    return error_response(e)

import types

from flask import abort

from app.api.helper import response, check_request
from app.api.image.helper import allowed_file, upload_file, remove_file
from app.api.validators import is_valid_email, is_registered, validate_password, validate_username
from app.models import User


def profile_error_response(errors):
    return response(False, 200, errors=errors)


def get_form_data(request):
    photo = request.files['photo'] if 'photo' in request.files else None
    remove_photo = (False, True)[int(request.form.get('removePhoto', 0))]
    name = request.form.get('name', None)
    email = request.form.get('email', None)
    password = request.form.get('password', '')

    if None in (name, email):
        abort(400, "Wrong request parameters.")

    return types.SimpleNamespace(photo=photo, removePhoto=remove_photo, name=name, email=email, password=password)


def get_json_data(request):
    mandatory_fields = {'photo', 'removePhoto', 'name', 'email', 'password'}
    return check_request(request, mandatory_fields)


def validate_profile_fields(data):
    errors = {}
    check_email = True

    if data.photo and not allowed_file(data.photo):
        errors['photo'] = 'Неверный формат файла.'

    validate_username(data.name, errors)

    if not is_valid_email(data.email):
        errors['email'] = 'Неправильный формат адреса.'
        check_email = False

    if not data.own_email and check_email and is_registered(data.email):
        errors['email'] = f"Пользователь с таким адресом уже зарегистрирован."

    if data.password:
        validate_password(data.password, errors)

    return errors if errors else None


def update_profile(user_id, data):
    user = User.query.get(user_id)

    if data.photo:
        try:
            user.photo = upload_file(data.photo)
        except OSError as e:
            abort(500, e)

    if data.removePhoto and user.photo is not None:
        remove_file(user.photo)
        user.photo = None

    if user.name != data.name:
        user.name = data.name

    if user.email != data.email:
        user.email = data.email

    if data.password:
        user.password = data.password

    user.save()

    return response(True, 200)


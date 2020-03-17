import types
from functools import wraps

from flask import g

from app.api.helper import response
from app.api.validators import validate_email_and_user_is_not_registered, validate_password
from app.models import User, Post


def login_response(user):
    return response(True, 200, payload=user_dto(user))


def login_error_response(message=None, errors=None):
    return response(False, 400, message=message, errors=errors)


def authorized_user_response(user_id):
    return login_response(User.query.get(user_id))


def unauthorized_user_response():
    return response(False, 200)


def logout_response(email):
    return response(True, 200, message=f"User '{email}' successfully logged out." if email else None)


def auth_required(f):
    """
    Decorator function to ensure that a resource is accessed only by authenticated users
    with valid credentials
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = g.user
        if not user:
            return response(False, 401, message='Authorization required.')
        return f(types.SimpleNamespace(**user), *args, **kwargs)
    return wrapper


def validate_login_request(data):
    errors = {}
    validate_email_and_user_is_not_registered(data, errors)
    validate_password(data, errors)

    if not errors:
        user = User.get_by_email(data.e_mail)
        if not user.is_valid_password(data.password):
            errors['password'] = "Either username or password are incorrect."
        else:
            return None, user

    return errors, None


def is_authorized():
    return True if g.user else False


def get_posts_awaiting_moderation():
    """
    Counts total number of posts to be moderated by any moderator, e.g.
      `isActive = 1` AND `moderationStatus = NEW` AND `moderatedBy = NULL`
    Query:
      SELECT COUNT (*) FROM posts p WHERE p.is_active = 1 AND p.moderation_status = 'NEW' AND p.moderator_id IS NULL
    :return: int Total amount of posts to be moderated
    """
    return Post.query.filter(
        Post.is_active,
        Post.moderation_status == 'NEW',
        Post.moderator_id.is_(None)).count()


def user_dto(user):
    dto = {
        'id': user.id,
        'name': user.name,
        'photo': user.photo,
        'email': user.email,
    }

    if user.is_moderator:
        dto['moderation'] = True
        dto['settings'] = True
        dto['moderationCount'] = get_posts_awaiting_moderation()

    return {'user': dto}

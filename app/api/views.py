from flask import Blueprint, make_response, jsonify, abort, request

from app import app
from app.api.auth.helper import auth_required
from app.api.helper import (
    error_response,
    check_request,
    process_moderation_request,
    is_valid_settings_request,
    response,
    save_settings,
    validate_comment_request, comment_error_response, comment_response, notify_comment_added)
from app.models import Post, Settings, Comment

api = Blueprint('api', __name__)


@api.route('/api/init', methods=['GET'])
def get_info():
    return make_response(jsonify(app.config['PROPERTIES']), 200)


@api.route('/api/moderation', methods=['POST'])
@auth_required
def moderate(user):
    if not user.is_moderator:
        abort(403, "You're not not allowed to moderate posts.")

    mandatory_fields = {'post_id', 'decision'}
    decisions = {'accept': 'ACCEPTED', 'decline': 'DECLINED'}

    data = check_request(request, mandatory_fields)
    decision = data.decision.lower()

    if decision not in decisions:
        abort(400, "Wrong decision type. Types allowed: 'accept', 'decline'.")

    post = Post.query.get_or_404(data.post_id, f"Post with id={data.post_id} not found.")

    return process_moderation_request(post, user.id, decisions[decision])


@api.route('/api/settings', methods=['GET'])
def get_settings():
    map_value = {"YES": True, "NO": False}
    settings = {option.code: map_value[option.value] for option in Settings.query.all()}
    return make_response(jsonify(settings), 200)


@api.route('/api/settings', methods=['PUT'])
@auth_required
def put_settings(user):
    if not user.is_moderator:
        abort(403, "You're not not allowed to change global site's settings.")

    mandatory_fields = {'MULTIUSER_MODE', 'POST_PREMODERATION', 'STATISTICS_IS_PUBLIC'}
    data = check_request(request, mandatory_fields)

    if not is_valid_settings_request(data):
        abort(400, "Wrong value type for one of the options. Only 'true' or 'false' are allowed.")

    save_settings(data)

    return response(True, 200)


@api.route('/api/comment', methods=['POST'])
@auth_required
def add_comment(user):
    mandatory_fields = {'post_id', 'parent_id', 'text'}
    data = check_request(request, mandatory_fields)
    errors = validate_comment_request(data)

    if errors:
        return comment_error_response(errors)

    comment = Comment(
        user_id=user.id,
        post_id=data.post_id,
        parent_id=data.parent_id if data.parent_id else None,
        text=data.text
    )

    comment = comment.save()

    notify_comment_added(comment)

    return comment_response(comment)


@api.errorhandler(Exception)
def handle_400_error(e):
    return error_response(e)

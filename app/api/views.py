from flask import Blueprint, make_response, jsonify, abort, request

from app import app
from app.api.auth.helper import auth_required
from app.api.helper import error_response, check_request, process_moderation_request
from app.models import Post

api = Blueprint('api', __name__)


@api.route('/api/init', methods=['GET'])
def get_info():
    return make_response(jsonify(app.config['PROPERTIES'])), 200


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


@api.errorhandler(400)
def handle_400_error(e):
    return error_response(e)


@api.errorhandler(403)
def handle_403_error(e):
    return error_response(e)

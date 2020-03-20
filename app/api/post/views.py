from flask import Blueprint, abort, request

from app.api.auth.helper import auth_required
from app.api.helper import response, error_response, check_request
from app.api.post.helper import (
    posts_response,
    post_response,
    get_active_posts,
    paginate,
    filter_posts,
    get_my_posts,
    get_moderated_posts,
    posts_processor,
    moderated_posts_processor,
    process_vote_and_get_response, validate_add_post_request, add_post_error_response, save_post, add_post_response)
from app.models import Post

api_post = Blueprint('api_post', __name__)


@api_post.route('/api/post', methods=['GET'])
def get_posts():
    offset = request.args.get('offset', None, type=int)
    limit = request.args.get('limit', None, type=int)
    mode = request.args.get('mode', None, type=str)

    if None in (offset, limit, mode):
        abort(400, "Wrong request parameters.")

    if mode.lower() not in ['recent', 'popular', 'best', 'early']:
        abort(400, "Wrong mode. Modes allowed: 'recent', 'popular', 'best', 'early'.")

    posts, posts_total = paginate(offset=offset, limit=limit, items=get_active_posts(mode=mode))

    return posts_response(processor=posts_processor, items=posts, total=posts_total)


@api_post.route('/api/post/<string:request_type>', methods=['GET'])
def get_filtered_posts(request_type):
    """
    There're 3 request types allowed: /api/post/{search, byDate, byTag}

    Request parameters: `offset`, `limit` & parameter that depends on the request type:
        `search` > `query`,
        `byDate` > `date`,
        `byTag` > `tag`
    """
    request_type = request_type.lower()
    request_types = {'search': 'query', 'bydate': 'date', 'bytag': 'tag'}

    if request_type and request_type not in request_types.keys():
        abort(400, "Wrong request type. Types allowed: 'search', 'byDate', 'byTag'.")

    query_type = request_types[request_type]

    offset = request.args.get('offset', None, type=int)
    limit = request.args.get('limit', None, type=int)
    query = request.args.get(query_type, None, type=str)

    if None in (offset, limit, query):
        abort(400, "Wrong request parameters.")

    filtered_posts = filter_posts(query=query.lower(), query_type=query_type, items=get_active_posts())

    posts, posts_total = paginate(offset=offset, limit=limit, items=filtered_posts)

    return posts_response(processor=posts_processor, items=posts, total=posts_total)


@api_post.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id, f"There's no post with id={post_id}.")
    post.view_count += 1
    post.save()
    return post_response(post)


@api_post.route('/api/post/my', methods=['GET'])
@auth_required
def my_posts(user):
    offset = request.args.get('offset', None, type=int)
    limit = request.args.get('limit', None, type=int)
    status = request.args.get('status', None, type=str)

    if None in (offset, limit, status):
        abort(400, "Wrong request parameters.")

    status = status.lower()

    if status not in {'inactive', 'pending', 'declined', 'published'}:
        abort(400, "Wrong status. Statuses allowed: 'inactive', 'pending', 'declined', 'published'.")

    posts, posts_total = paginate(
        offset=offset,
        limit=limit,
        items=get_my_posts(user, status)
    )

    return posts_response(processor=posts_processor, items=posts, total=posts_total)


@api_post.route('/api/post/moderation', methods=['GET'])
@auth_required
def moderated_posts(user):
    if not user.is_moderator:
        abort(403, "You're not not allowed to moderate posts.")

    offset = request.args.get('offset', None, type=int)
    limit = request.args.get('limit', None, type=int)
    status = request.args.get('status', None, type=str)

    if None in (offset, limit, status):
        abort(400, "Wrong request parameters.")

    status = status.lower()

    if status not in {'new', 'declined', 'accepted'}:
        abort(400, "Wrong status. Statuses allowed: 'new', 'declined', 'accepted'.")

    posts, posts_total = paginate(
        offset=offset,
        limit=limit,
        items=get_moderated_posts(user, status)
    )

    return posts_response(processor=moderated_posts_processor, items=posts, total=posts_total)


@api_post.route('/api/post/<string:vote_type>', methods=['POST'])
@auth_required
def vote_post(user, vote_type):
    vote_type = vote_type.lower()
    vote_types = {'like': 1, 'dislike': -1}

    if vote_type and vote_type not in vote_types:
        abort(400, "Wrong vote type. Types allowed: 'like', 'dislike'.")

    mandatory_fields = {'post_id', }
    data = check_request(request, mandatory_fields)
    post = Post.active_posts.filter_by(id=data.post_id).first()

    if not post:
        abort(404, f"Пост с идентификатором {data.post_id} не найден.")

    return process_vote_and_get_response(post, user, vote_types[vote_type])


"""
New Post
"""


@api_post.route('/api/post', methods=['POST'])
@auth_required
def add_post(user):
    mandatory_fields = {'time', 'active', 'title', 'text', 'tags'}
    data = check_request(request, mandatory_fields)
    errors = validate_add_post_request(data)

    if errors:
        return add_post_error_response(errors)

    saved_post = save_post(post=None, user_id=user.id, data=data)

    # Notify post was successfully created via Telegram

    return add_post_response(saved_post.id)


@api_post.errorhandler(400)
def handle_400_error(e):
    return error_response(e)


@api_post.errorhandler(403)
def handle_403_error(e):
    return error_response(e)


@api_post.errorhandler(404)
def handle_404_error(e):
    return response(False, 404, message=f"Post not found. {e.description}")

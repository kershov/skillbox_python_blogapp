from flask import Blueprint, abort, request

from app.api.helper import response, error_response
from app.api.post.helper import posts_response, post_response, get_active_posts, paginate, filter_posts
from app.models import Post

api_post = Blueprint('api_post', __name__)


@api_post.route('/api/post', methods=['GET'])
def get_posts():
    offset = request.args.get('offset', None, type=int)
    limit = request.args.get('limit', None, type=int)
    mode = request.args.get('mode', None, type=str)

    if None in (offset, limit, mode):
        abort(400, "Bad request.")

    if mode.lower() not in ['recent', 'popular', 'best', 'early']:
        abort(400, "Wrong mode. Modes allowed: 'recent', 'popular', 'best', 'early'.")

    posts, posts_total = paginate(offset=offset, limit=limit, items=get_active_posts(mode=mode))

    return posts_response(posts, posts_total)


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
        abort(400, "Bad request.")

    filtered_posts = filter_posts(query=query.lower(), query_type=query_type, items=get_active_posts())

    posts, posts_total = paginate(offset=offset, limit=limit, items=filtered_posts)

    return posts_response(posts, posts_total)


@api_post.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    return post_response(Post.query.get_or_404(post_id, f"There's no post with id={post_id}."))


@api_post.errorhandler(400)
def handle_400_error(e):
    return error_response(e)


@api_post.errorhandler(404)
def handle_404_error(e):
    return response(False, 404, message=f"Post not found. {e.description}")

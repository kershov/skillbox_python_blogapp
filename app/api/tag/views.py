from flask import Blueprint, request

from app.api.tag.helper import tags_response
from app.models import Tag

api_tag = Blueprint('api_tag', __name__)


@api_tag.route('/api/tag', methods=['GET'])
def get_tags():
    query = request.args.get('query', None, type=str)

    return tags_response(Tag.get_weighted_tags(query))

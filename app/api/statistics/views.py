from flask import Blueprint, abort, g

from app.api.helper import response
from app.api.statistics.helper import get_statistics
from app.models import Settings

api_statistics = Blueprint('api_statistics', __name__)


@api_statistics.route('/api/statistics/<string:stats_type>', methods=['GET'])
def stats(stats_type):
    user = g.user
    is_stats_public = Settings.get_by_code('STATISTICS_IS_PUBLIC')

    stats_type = stats_type.lower()
    stats_types = {'my', 'all'}

    if stats_type and stats_type not in stats_types:
        abort(400, "Wrong request type. Types allowed: 'my', 'all'.")

    # Authorized and...
    if user:
        # ... stats_type = all
        if is_stats_public and stats_type == 'all':
            return get_statistics(user=None)
        # ... stats_type = my
        return get_statistics(user=user)

    # Unauthorized + stats is public >> show public stats
    if is_stats_public:
        return get_statistics(user=user)

    # Unauthorized + stats is private >> 401
    return response(False, 401)

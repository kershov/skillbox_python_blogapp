from flask import jsonify, make_response

from app.models import Post, Vote


def get_statistics(user=None):
    user_id = user['id'] if user else None

    data = {
        'postsCount': Post.count_by_author(user_id),
        'likesCount': Vote.count_by_user_and_vote_type(user_id, 'like'),
        'dislikesCount': Vote.count_by_user_and_vote_type(user_id, 'dislike'),
        'viewsCount': Post.count_views_by_user(user_id),
        'firstPublication': Post.get_first_publication_date_by_user(user_id)
    }

    return make_response(jsonify(data), 200)

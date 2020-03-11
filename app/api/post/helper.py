from flask import jsonify, make_response

from app import db
from app.api.helper import time_utc_to_local, clear_html_tags
from app.models import Vote, Post, Comment, filter_by_active_posts, Tag


def post_response(post):
    return make_response(jsonify(full_post_dto(post))), 200


def posts_response(items, total):
    return make_response(jsonify({
        'count': total,
        'posts': [
            simple_post_dto(post, int(num_likes), int(num_dislikes), int(num_comments))
            for post, num_likes, num_dislikes, num_comments in items
        ]
    })), 200


def get_active_posts(mode=None):
    orders = {
        'recent': (db.desc(Post.time),),
        'popular': (db.desc('commentCount'), db.desc(Post.time)),
        'best': (db.desc('likeCount'), db.desc(Post.time)),
        'early': (db.asc(Post.time),)
    }

    order = orders.get(mode, orders['recent'])

    likes = db.select([db.func.count(Vote.id)]).where(
        db.and_(Vote.value == 1, Vote.post_id == Post.id)
    ).as_scalar().label('likeCount')

    dislikes = db.select([db.func.count(Vote.id)]).where(
        db.and_(Vote.value == -1, Vote.post_id == Post.id)
    ).as_scalar().label('dislikeCount')

    comments = db.select([db.func.count(Comment.id)]).where(
        Comment.post_id == Post.id
    ).as_scalar().label('commentCount')

    return filter_by_active_posts(Post.query.with_entities(Post, likes, dislikes, comments)).order_by(*order)


def filter_posts(query=None, query_type=None, items=None):
    query_filters = {
        'query': db.or_(
            db.func.lower(Post.title).like(f'%{query}%'),
            db.func.lower(Post.text).like(f'%{query}%')
        ),
        'date': db.func.date(Post.time) == query,
        'tag': db.func.lower(Tag.name) == query,
    }

    if query_type == 'tag':
        items = items.join(Tag, Post.tags)

    return items.filter(query_filters[query_type])


def paginate(offset=0, limit=10, items=None):
    page = offset // limit + 1
    pagination = items.paginate(page=page, per_page=limit, error_out=False)
    return pagination.items, pagination.total


"""
Various Post DTOs
"""


def user_dto(user):
    return {
        'id': user.id,
        'name': user.name
    }


def comment_dto(comment):
    return {
        'id': comment.id,
        'text': comment.text,
        'time': time_utc_to_local(comment.time),
        'user': {
            **user_dto(comment.user),
            'photo': comment.user.photo,
        }
    }


def simple_post_dto(post, num_likes=None, num_dislikes=None, num_comments=None):
    return {
        **post_common_fields(post, num_likes=num_likes, num_dislikes=num_dislikes, num_comments=num_comments),
        'announce': clear_html_tags(post.text),
    }


def full_post_dto(post):
    return {
        **post_common_fields(post),
        'text': post.text,
        'comments': [comment_dto(comment) for comment in post.comments],
        'tags': [tag.name for tag in post.tags]
    }


def post_common_fields(post, num_likes=None, num_dislikes=None, num_comments=None):
    return {
        'id': post.id,
        'title': post.title,
        'time': time_utc_to_local(post.time),
        'user': user_dto(post.author),
        'viewCount': post.view_count,
        'commentCount': num_comments if num_comments else post.comment_count,
        'likeCount': num_likes if num_likes else post.likes,
        'dislikeCount': num_dislikes if num_dislikes else post.dislikes,
    }

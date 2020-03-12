from flask import make_response, jsonify

from app import db
from app.models import Post


def calendar_response(year):
    return make_response(jsonify(calendar_dto(year)), 200)


def get_years():
    years = Post.active_posts \
        .group_by('years') \
        .order_by(db.desc(Post.time)) \
        .values(db.func.year(Post.time).label('years'))

    return list(zip(*years)).pop()


def posts_by_date(year):
    query = Post.active_posts.with_entities(
        db.func.date_format(Post.time, '%Y-%m-%d').label('date'),
        db.func.count('*').label('count')
    ).group_by('date').order_by(db.desc(Post.time))

    posts = query if not year else query.filter(db.func.year(Post.time) == year)

    return {post.date: post.count for post in posts.all()}


def calendar_dto(year):
    return {
        'years': get_years(),
        'posts': posts_by_date(year)
    }

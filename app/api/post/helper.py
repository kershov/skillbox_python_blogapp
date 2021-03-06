from datetime import datetime

from flask import jsonify, make_response, request

from app import db
from app.api.helper import response
from app.api.validators import validate_title, validate_text
from app.helper import clear_html_tags
from app.models import Vote, Post, Comment, Tag
from app.tg.client import send_telegram_message
from app.tg.helper import escape


def post_response(post):
    return make_response(jsonify(full_post_dto(post)), 200)


def posts_response(processor, items, total):
    return make_response(jsonify({
        'count': total,
        'posts': processor(items)
    }), 200)


def get_active_posts(mode=None):
    return get_posts(mode).filter(*Post.active_posts_filter())


def get_posts(mode=None):
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

    return Post.query.with_entities(Post, likes, dislikes, comments).order_by(*order)


def get_my_posts(user, status=None):
    statuses = {
        'inactive': (db.not_(Post.is_active),),
        'pending': (Post.is_active, Post.moderation_status == 'NEW'),
        'declined': (Post.is_active, Post.moderation_status == 'DECLINED'),
        'published': (Post.is_active, Post.moderation_status == 'ACCEPTED'),
    }

    filter_criteria = statuses.get(status, statuses['inactive'])

    return get_posts().filter(Post.user_id == user.id).filter(*filter_criteria)


def get_moderated_posts(user, status=None):
    statuses = {
        'new': (Post.moderation_status == 'NEW', Post.moderator_id.is_(None)),
        'declined': (Post.moderation_status == 'DECLINED', Post.moderator_id == user.id),
        'accepted': (Post.moderation_status == 'ACCEPTED', Post.moderator_id == user.id),
    }

    filter_criteria = statuses.get(status, statuses['new'])

    return Post.query.filter(Post.is_active, *filter_criteria).order_by(db.desc(Post.time))


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
    offset = offset if offset >= 0 else 0
    limit = limit if limit > 0 else 10
    page = offset // limit + 1
    pagination = items.paginate(page=page, per_page=limit, error_out=False)
    return pagination.items, pagination.total


"""
Votes: Likes & Dislikes
"""


def process_vote_and_get_response(post, user, value):
    vote = Vote.get_by_post_and_user(post.id, user.id)

    if vote:
        if vote.value == value:
            return response(False, 200)
        vote.delete()

    vote = Vote(post_id=post.id, user_id=user.id, value=value)
    vote.save()

    return response(True, 200)


"""
Add Post
"""


def add_post_response(post_id):
    return response(False, 200, message=f'Post successfully saved with id={post_id}.')


def add_post_error_response(errors):
    return response(False, 400, errors=errors)


def validate_add_post_request(data):
    errors = {}
    check_tags = True

    validate_title(data.title, errors)
    validate_text(data.text, errors)

    if data.active not in [0, 1]:
        errors['active'] = 'Неверное значение. Разрешенные значения: 0, 1.'

    if not isinstance(data.tags, list):
        errors['tags'] = 'Неверное значение. Необходимо передать список тегов.'
        check_tags = False

    if check_tags and not all(isinstance(tag, str) for tag in data.tags):
        errors['tags'] = 'Неверное значение. Теги должны быть строками.'

    try:
        datetime.strptime(data.time, "%Y-%m-%dT%H:%M")
    except ValueError:
        errors['time'] = 'Неверный формат даты. Допустимый формат: yyyy-mm-ddThh:mm.'

    return errors


def save_post(post, author, data):
    post_to_save = post if post else Post()

    now = datetime.now()
    post_time = datetime.strptime(data.time, "%Y-%m-%dT%H:%M")

    post_to_save.title = data.title
    post_to_save.text = data.text
    post_to_save.is_active = data.active
    post_to_save.time = now if post_time <= now else post_time
    post_to_save.author = author

    if post is None or (author == post_to_save.author and not author.is_moderator):
        post_to_save.moderation_status = 'NEW'

    if data.tags:
        update_post_tags(post_to_save.tags, data.tags)

    return post_to_save.save()


def update_post_tags(post_tags, updated_tags):
    proposed_tags = set(updated_tags)
    current_tags = set(tag.name for tag in post_tags)

    if current_tags != proposed_tags:
        tags_to_delete = current_tags - proposed_tags
        tags_to_add = proposed_tags - current_tags

        if tags_to_delete:
            update_tag_list(post_tags.remove, tags_to_delete)

        if tags_to_add:
            update_tag_list(post_tags.append, tags_to_add)


def update_tag_list(list_action, items):
    _ = [list_action(Tag.save_tag(tag_name)) for tag_name in items]


def notify_post_added(post):
    email = escape(post.author.email)
    post_id = post.id
    post_title = escape(post.title)
    host = request.host_url

    message = f"Пользователь *{email}* добавил новый или изменил ранее опубликованный пост " \
              f"\"[{post_title}]({host}post/{post_id})\" \\(Post ID: {post_id}\\)\\.\n\n\\#модерация"
    send_telegram_message(message)


"""
Various Post Processors
"""


def posts_processor(items):
    return [
        simple_post_dto(post, int(num_likes), int(num_dislikes), int(num_comments))
        for post, num_likes, num_dislikes, num_comments in items
    ]


def moderated_posts_processor(items):
    return [moderated_post_dto(post) for post in items]


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
        'time': datetime.strftime(comment.time, "%Y-%m-%d %H:%M"),
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
        'time': datetime.strftime(post.time, "%Y-%m-%d %H:%M"),
        # TODO: BUG: Frontend app doesn't consider this field properly while editing a post
        'active': post.is_active,
        'user': user_dto(post.author),
        'viewCount': post.view_count,
        'commentCount': num_comments if num_comments else post.comment_count,
        'likeCount': num_likes if num_likes else post.likes,
        'dislikeCount': num_dislikes if num_dislikes else post.dislikes,
    }


def moderated_post_dto(post):
    return {
        'id': post.id,
        'time': datetime.strftime(post.time, "%Y-%m-%d %H:%M"),
        'user': user_dto(post.author),
        'title': post.title,
        'announce': clear_html_tags(post.text)
    }

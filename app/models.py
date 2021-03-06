import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.hybrid import hybrid_property

from app import db, app, bcrypt
from app.api.auth.captcha.helper import generate_captcha_code, generate_base64_image


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    is_moderator = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.Text, nullable=True)
    reg_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    _password = db.Column('password', db.String(255), nullable=False)

    """
    Relations
    """
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys="Post.user_id")
    moderated_posts = db.relationship('Post', backref='moderator', lazy=True, foreign_keys="Post.moderator_id")
    comments = db.relationship('Comment', backref='user', lazy=True, foreign_keys="Comment.user_id")
    votes = db.relationship('Vote', backref='user', lazy=True, foreign_keys="Vote.user_id")

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password, app.config['BCRYPT_LOG_ROUNDS']).decode('utf-8')

    def is_valid_password(self, password):
        return bcrypt.check_password_hash(self._password, password)

    def save(self):
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        db.session.refresh(self)
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_code(code: str):
        code = code.strip()
        if not code:
            raise ValueError("Code field can't be blank.")
        return User.query.filter_by(code=code).first()

    @staticmethod
    def create_user(email, password):
        user = User(email=email, name=email, password=password)
        return user.save()

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', name='{self.name}', reg_time='{self.reg_time}')>"


post_tags = db.Table('posts_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True))


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    moderation_status = db.Column(db.String(10), nullable=False)
    view_count = db.Column(db.Integer, nullable=False, default=0)

    """
    Relations
    """
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    votes = db.relationship('Vote', backref='post', lazy=True, foreign_keys="Vote.post_id")
    comments = db.relationship('Comment', backref='post', lazy=True, foreign_keys="Comment.post_id")
    tags = db.relationship('Tag', secondary=post_tags,
                           backref=db.backref('posts', lazy='dynamic'),
                           lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

    def save(self):
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        db.session.refresh(self)
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    """
    Hybrid properties
    """

    @hybrid_property
    def comment_count(self):
        return len(self.comments)

    @hybrid_property
    def likes(self):
        return sum(1 for vote in self.votes if vote.value == 1)

    @hybrid_property
    def dislikes(self):
        return sum(1 for vote in self.votes if vote.value == -1)

    @hybrid_property
    def active_posts(self):
        return self.query.filter(*Post.active_posts_filter())

    @staticmethod
    def active_posts_filter():
        return Post.is_active, Post.moderation_status == 'ACCEPTED', Post.time <= datetime.now()

    @staticmethod
    def count_by_author(user_id=None):
        f = (Post.user_id is not None, ) if not user_id else (Post.user_id == user_id, )
        return Post.query.filter(*f).count()

    @staticmethod
    def count_views_by_user(user_id=None):
        f = (Post.user_id is not None,) if not user_id else (Post.user_id == user_id,)
        return int(Post.query.filter(*f).value(db.func.sum(Post.view_count)))

    @staticmethod
    def get_first_publication_date_by_user(user_id):
        f = (Post.user_id is not None,) if not user_id else (Post.user_id == user_id,)
        return Post.query.filter(*f).value(db.func.date_format(db.func.min(Post.time), '%Y-%m-%d %H:%m'))

    def __repr__(self):
        return f"<Post(id='{self.id}', title='{self.title[:25]}...', is_active={self.is_active}, " \
               f"moderation_status='{self.moderation_status}', view_count='{self.view_count}', time='{self.time}')>"


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name
        self.base_weight = 0.0
        self.weight = 0.0

    def save(self):
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        db.session.refresh(self)
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    """
    Relations: managed by Post.posts
    """

    """
    Hybrid properties
    """

    @hybrid_property
    def posts_tagged(self):
        return Post.query.join(Post.tags).filter(Tag.id == self.id, *Post.active_posts_filter())

    @hybrid_property
    def active_tags(self):
        return Tag.query.with_entities(Tag, db.func.count('*').label('cnt')).join(Post.tags) \
            .filter(*Post.active_posts_filter()) \
            .distinct() \
            .group_by(Tag.id) \
            .order_by(db.desc('cnt'), db.asc(Tag.name))

    @staticmethod
    def get_weighted_tags(query=None):
        active_tags = Tag.active_tags.all()
        most_frequent_tag, _ = Tag.active_tags.first()

        for tag, posts_tagged in active_tags:
            tag.base_weight = posts_tagged / Post.active_posts.count()

        for tag, _ in active_tags:
            tag.weight = tag.base_weight / most_frequent_tag.base_weight

        return active_tags if not query else list(
            filter(lambda item: query.lower() in item[0].name.lower(), active_tags))

    @staticmethod
    def save_tag(name):
        tag = Tag.query.filter(db.func.lower(Tag.name) == name.lower()).first()
        return tag if tag else Tag(name).save()

    def __new__(cls, *args, **kwargs):
        return super(Tag, cls).__new__(cls)

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', " \
               f"posts_tagged__total={self.posts.count()}, posts_tagged__active={self.posts_tagged.count()})>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    """
    Relations
    """
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    """
    Self-reference
    
    Ref: 
        https://docs.sqlalchemy.org/en/13/orm/self_referential.html#self-referential
        
    Option: 
        parent = db.relationship('Comment', backref='children', remote_side=[id], lazy=True,)
    """
    children = db.relationship("Comment", backref=db.backref('parent', remote_side=[id]), lazy=True)

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)

    def save(self):
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        db.session.refresh(self)
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Comment(id={self.id}, parent_id={self.parent_id}, user_id={self.user_id}, post_id={self.post_id}, " \
               f"text='{self.text[:25]}...', time='{self.time}')>"


class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    value = db.Column(db.SmallInteger, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Vote, self).__init__(*args, **kwargs)

    def save(self):
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        db.session.refresh(self)
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_post_and_user(post_id, user_id):
        return Vote.query.filter_by(post_id=post_id, user_id=user_id).first()

    @staticmethod
    def count_by_user_and_vote_type(user_id, vote_type='like'):
        vote_types = {'like': 1, 'dislike': -1}
        filter_criteria = (Vote.user_id is not None,) if not user_id else (Vote.user_id == user_id,)
        return Vote.query.filter(Vote.value == vote_types[vote_type], *filter_criteria).count()

    def __repr__(self):
        return f"<Vote(id={self.id}, post_id={self.post_id}, user_id={self.user_id}, value='{self.value}', " \
               f"time='{self.time}')>"


class CaptchaCode(db.Model):
    __tablename__ = "captcha_codes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(255), nullable=False)
    secret_code = db.Column(db.String(255), unique=True, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init__(self, *args, **kwargs):
        super(CaptchaCode, self).__init__(*args, **kwargs)
        self.code = generate_captcha_code()
        self.secret_code = str(uuid.uuid4())
        self.image_base_64 = generate_base64_image(self.code)

    def save(self):
        db.session.add(self)

        # At this point, the object has been pushed to the DB,
        # and has been automatically assigned a unique PK id
        db.session.flush()
        db.session.commit()

        # Updates given object in the session with its state in the DB
        db.session.refresh(self)

        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_valid_code(self, user_code):
        return self.code == user_code

    @staticmethod
    def get_by_secret_code(secret_code):
        return CaptchaCode.query.filter_by(secret_code=secret_code).first()

    @staticmethod
    def delete_outdated_captchas(ttl=None):
        ttl = ttl or 1
        time = datetime.now() - timedelta(hours=ttl)

        return CaptchaCode.query.filter(CaptchaCode.time <= time).delete()

    def json(self):
        return {
            'secret': self.secret_code,
            'image': self.image_base_64
        }

    def __repr__(self):
        return f"<CaptchaCode(id='{self.id}', code='{self.code}', reg_time='{self.time}')>"


class Settings(db.Model):
    __tablename__ = "global_settings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.String(5), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_code(code, as_is=False):
        option = Settings.query.filter_by(code=code).first().value
        return option if as_is else {'YES': True, 'NO': False}.get(option)

    def __repr__(self):
        return f"<Setting(id='{self.id}', code='{self.code}', name='{self.name}', value='{self.value}'>"

from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    is_moderator = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.Text, nullable=True)
    reg_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    """
    Relations
    """
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys="Post.user_id")
    moderated_posts = db.relationship('Post', backref='moderator', lazy=True, foreign_keys="Post.moderator_id")
    comments = db.relationship('Comment', backref='comment', lazy=True, foreign_keys="Comment.user_id")
    votes = db.relationship('Vote', backref='user', lazy=True, foreign_keys="Vote.user_id")

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', name='{self.name}', reg_time='{self.reg_time}')>"


post_tags = db.Table('posts_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True))


class Post(db.Model):
    """
    Table schema
    """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    moderation_status = db.Column(db.String(10), nullable=False)
    view_count = db.Column(db.Integer, nullable=False)

    """
    Relations
    """
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    votes = db.relationship('Vote', backref='post', lazy=True, foreign_keys="Vote.post_id")
    comments = db.relationship('Comment', backref='post', lazy=True, foreign_keys="Comment.post_id")
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery', backref=db.backref('posts', lazy=True))

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Post(id='{self.id}', title='{self.title[:25]}...', is_active={self.is_active}, " \
               f"moderation_status='{self.moderation_status}', view_count='{self.view_count}', time='{self.time}')>"


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    """
    Relations: managed by Post.posts
    """

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', posts_tagged={len(self.posts)})>"


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
        db.session.commit()

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
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Vote(id={self.id}, post_id={self.post_id}, user_id={self.user_id}, value='{self.value}', " \
               f"time='{self.time}')>"


class CaptchaCode(db.Model):
    """
    Table schema
    """
    __tablename__ = "captcha_codes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(255), nullable=False)
    secret_code = db.Column(db.String(255), unique=True, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init__(self, *args, **kwargs):
        super(CaptchaCode, self).__init__(*args, **kwargs)
        self.image_base_64 = None  # To be user later
        # TODO: Methods needed:
        #   setCode(CaptchaUtils.getRandomCode(codeLength))
        #   setSecretCode(UUID.randomUUID().toString())
        #   setImageBase64(CaptchaUtils.getImageBase64(getCode(), fontSize))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_valid_code(self, user_code):
        return self.code == user_code

    def __repr__(self):
        return f"<CaptchaCode(id='{self.id}', code='{self.code}', reg_time='{self.time}')>"


class Settings(db.Model):
    """
    Table schema
    """
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

    def update(self, code=None, name=None, value=None):
        if code is not None:
            self.code = code
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Setting(id='{self.id}', code='{self.code}', name='{self.name}', value='{self.value}'>"

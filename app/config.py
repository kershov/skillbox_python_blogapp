import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """
    Base application configuration
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(base_dir, 'db_repository')   # https://habr.com/ru/post/196810/
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    PERMANENT_SESSION_LIFETIME = timedelta(days=5)
    BCRYPT_LOG_ROUNDS = 8
    PROPERTIES = {
        "title": "BlogApp",
        "subtitle": "Skillbox Graduation Work: Simple Blog Engine",
        "phone": "+7 000 765-4321",
        "email": "konstantin.ershov@gmail.com",
        "copyright": "Konstantin Ershov",
        "copyrightFrom": "2020"
    }
    CAPTCHA = {
        "length": 6,        # chars
        "ttl": 1,           # hours
        "font-size": 18
    }
    PASSWORD = {
        "min": 6,
        "max": 255
    }
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


class DevelopmentConfig(BaseConfig):
    """
    Development application configuration
    """
    DEBUG = True


class ProductionConfig(BaseConfig):
    """
    Production application configuration
    """
    DEBUG = True

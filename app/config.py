import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """
    Base application configuration
    """
    DEBUG = False
    STATIC_RESOURCES_DIR = os.path.join(base_dir, 'resources', 'static')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
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
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024                    # 5 megabytes

    CAPTCHA = {
        "length": 6,        # chars
        "ttl": 1,           # hours
        "font-size": 18
    }
    USERNAME = {"min": 3, "max": 255}
    PASSWORD = {"min": 6, "max": 255}
    TITLE = {'min': 5, 'max': 255}
    TEXT = {'min': 10, 'max': 5000}


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

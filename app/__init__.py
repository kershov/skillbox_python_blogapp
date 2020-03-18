import os

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Initialize application
from app.helper import create_upload_dir

app = Flask(__name__, static_folder=None, template_folder='resources/templates')
app.url_map.strict_slashes = False

# Load Environment variables for further processing in app.config
load_dotenv(find_dotenv())

# app configuration
app_settings = os.getenv(
    'APP_SETTINGS',
    'app.config.DevelopmentConfig'
)
app.config.from_object(app_settings)
app.config['APP_ROOT_DIR'] = os.path.dirname(app.instance_path)
app.config['UPLOAD_DIR'] = os.path.join(app.config['APP_ROOT_DIR'], os.getenv('UPLOAD_DIR'))
create_upload_dir(app.config['UPLOAD_DIR'])

# Initialize Flask Sql Alchemy
db = SQLAlchemy(app)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Initialize Mail
mail = Mail(app)

# Import the application views
from app import views

# Register API Endpoints
from app.api.views import api
from app.api.post.views import api_post
from app.api.tag.views import api_tag
from app.api.calendar.views import api_calendar

from app.api.auth.views import api_auth
from app.api.auth.captcha.views import api_captcha
from app.api.auth.register.views import api_register
from app.api.auth.restore.views import api_restore_password
from app.api.image.views import api_image

app.register_blueprint(api)
app.register_blueprint(api_post)
app.register_blueprint(api_tag)
app.register_blueprint(api_calendar)

app.register_blueprint(api_auth)
app.register_blueprint(api_captcha)
app.register_blueprint(api_register)
app.register_blueprint(api_restore_password)
app.register_blueprint(api_image)

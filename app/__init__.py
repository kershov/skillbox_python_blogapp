import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize application
app = Flask(__name__, static_folder=None, template_folder='resources/templates')
app.url_map.strict_slashes = False

# Load Environment variables for further processing in app.config
dotenv_path = os.path.join(os.path.dirname(app.instance_path), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# app configuration
app_settings = os.getenv(
    'APP_SETTINGS',
    'app.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

# Initialize Flask Sql Alchemy
db = SQLAlchemy(app)

# Import the application views
from app import views

# Register API Endpoints
from app.api.init.views import api_init
from app.api.post.views import api_post
from app.api.tag.views import api_tag

app.register_blueprint(api_init)
app.register_blueprint(api_post)
app.register_blueprint(api_tag)

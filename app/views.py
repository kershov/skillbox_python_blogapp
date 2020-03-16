import os

from flask import render_template, send_from_directory, g, session

from app import app
from app.config import base_dir
from app.models import User


def send_static_resource(path):
    static_root = os.path.join(base_dir, "resources", "static")
    return send_from_directory(static_root, path)


@app.before_request
def before_request():
    g.user = User.get_by_email(session['email']) if 'email' in session else None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url_parts = path.split('/')

    if len(url_parts) > 1:
        if url_parts[1] in ['favicon.ico', 'default-1.png']:
            return send_static_resource(url_parts[1])

        if url_parts[0] in ['css', 'fonts', 'img', 'js']:
            return send_static_resource(path)

    return render_template("index.html")

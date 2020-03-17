from flask import render_template, g, session, send_from_directory

from app import app


@app.before_request
def before_request():
    g.user = session['user'] if 'user' in session else None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url_parts = path.split('/')

    if len(url_parts) > 0:
        if url_parts[0] in ['favicon.ico', 'default-1.png', 'css', 'fonts', 'img', 'js']:
            return send_from_directory(app.config['STATIC_RESOURCES_DIR'], path)

        if url_parts[0] == 'upload':
            return send_from_directory(app.config['APP_ROOT_DIR'], path)

    return render_template("index.html")

import os

from werkzeug.utils import secure_filename

from app import app
from app.helper import generate_random_string


def upload_file(file):
    upload_dir = app.config['UPLOAD_DIR']
    filename = secure_filename(file.filename)

    path = [generate_random_string().lower() for _ in range(3)]
    path = os.path.join(upload_dir, *path)

    os.makedirs(path, exist_ok=True)

    full_path = os.path.join(path, filename)
    file.save(full_path)

    return '/' + get_relative_path(upload_dir, full_path).replace('\\', '/')


def allowed_file(file):
    return '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_relative_path(base_path, path):
    return os.path.normpath(
        os.path.join(os.path.basename(base_path),
                     os.path.relpath(path, base_path)))

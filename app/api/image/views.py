from flask import Blueprint, request, abort

from app.api.auth.helper import auth_required
from app.api.helper import error_response
from app.api.image.helper import allowed_file, upload_file

api_image = Blueprint('api_image', __name__)


@api_image.route('/api/image', methods=['POST'])
@auth_required
def upload_image(user):
    if 'image' not in request.files:
        abort(400, 'Wrong request parameter.')

    file = request.files['image']

    if file.filename == '':
        abort(400, 'No file selected.')

    if not allowed_file(file):
        abort(400, 'Wrong file type. Only images allowed.')

    try:
        image_path = upload_file(file)
    except OSError as e:
        abort(500, e)
    else:
        return image_path, 200


@api_image.errorhandler(400)
def handle_400_error(e):
    return error_response(e)


@api_image.errorhandler(500)
def handle_500_error(e):
    return error_response(e)

from flask import Blueprint, make_response, jsonify

from app import app

api = Blueprint('api', __name__)


@api.route('/init', methods=['GET'])
def get_info():
    return make_response(jsonify(app.config['PROPERTIES']), 200)


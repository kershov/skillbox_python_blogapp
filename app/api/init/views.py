from flask import Blueprint, make_response, jsonify

from app import app

api_init = Blueprint('api_init', __name__)


@api_init.route('/api/init', methods=['GET'])
def get_info():
    return make_response(jsonify(app.config['PROPERTIES'])), 200

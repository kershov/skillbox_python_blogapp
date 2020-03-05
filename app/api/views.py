from random import randint

from flask import Blueprint, make_response, jsonify

from app import app

api = Blueprint('api', __name__)


@api.route('/init', methods=['GET'])
def get_info():
    return make_response(jsonify(app.config['PROPERTIES'])), 200


@api.route('/tag', methods=['GET'])
def get_tags():
    tags = {
        "tags": [
            {"name": "Tag 1", "weight": 0.994},
            {"name": "Tag 2", "weight": 0.88},
            {"name": "Tag 3", "weight": 0.3}
        ]
    }

    return make_response(jsonify(tags)), 200

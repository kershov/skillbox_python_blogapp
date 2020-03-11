from flask import make_response, jsonify


def tags_response(tags):
    return make_response(jsonify({
        'tags': [tag_dto(tag) for tag, _ in tags]
    })), 200


def tag_dto(tag):
    return {
        'name': tag.name,
        'weight': tag.weight
    }

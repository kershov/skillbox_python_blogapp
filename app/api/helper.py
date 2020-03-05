from flask import make_response, jsonify


def response(result, message, errors, status_code):
    """
    Helper method to make an Http response
    :param result: Result (True or False)
    :param message: Message
    :param errors: Errors if any
    :param status_code: Http status code
    :return:
    """
    return make_response(jsonify({
        'result': result,
        'message': message,
        'errors': errors,
    })), status_code

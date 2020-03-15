import types
import uuid

import pytz
from bs4 import BeautifulSoup
from flask import make_response, jsonify, abort

local_tz = pytz.timezone('Europe/Moscow')


def check_request(request, mandatory_fields: set):
    if not isinstance(mandatory_fields, set):
        raise TypeError("mandatory_fields has to be of type set.")

    if not mandatory_fields:
        raise ValueError("mandatory_fields has to have at least one field.")

    if 'application/json' not in request.content_type:
        abort(400, "Content-type must be 'application/json'.")

    if not request.data:
        abort(400, 'Request has no body.')

    data = request.get_json()

    if mandatory_fields != set(data):
        params = ', '.join(f"'{field}'" for field in mandatory_fields)
        abort(400, "Wrong body. Either one or more mandatory parameters are wrong, don't exist or misspelled. "
                   f"Mandatory parameters are: {params}.")

    return types.SimpleNamespace(**data)


def response(result, status_code, message=None, errors=None):
    """
    Helper method to make an Http response
    :param result: Result (True or False)
    :param status_code: Http status code
    :param message: Message
    :param errors: Errors if any
    :return:
    """

    resp = {
        'result': result,
        'status': status_code
    }

    if message:
        resp['message'] = message

    if errors:
        resp['errors'] = errors

    return make_response(jsonify(resp), status_code)


def clear_html_tags(text):
    return BeautifulSoup(text, features="html.parser").get_text()


def time_utc_to_local(utc_dt, time_format=None):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt.strftime(time_format) if time_format else local_dt.strftime(
        "%Y-%m-%d %H:%M")


def error_response(error):
    return response(False, error.code, message=f"{error.name}: {error.description}")


def generate_secret_code():
    return str(uuid.uuid4())

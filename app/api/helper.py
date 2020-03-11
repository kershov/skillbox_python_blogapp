import pytz
from bs4 import BeautifulSoup
from flask import make_response, jsonify

local_tz = pytz.timezone('Europe/Moscow')


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

    return make_response(jsonify(resp)), status_code


def clear_html_tags(text):
    return BeautifulSoup(text, features="html.parser").get_text()


def time_utc_to_local(utc_dt, time_format=None):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt.strftime(time_format) if time_format else local_dt.strftime(
        "%Y-%m-%d %H:%M")  # local_tz.normalize(local_dt)

import sys

import requests
from flask import Blueprint
from requests import HTTPError

from app import app
from app.tg.helper import async_request

telegram = Blueprint('telegram', __name__)


@async_request
def send_telegram_message(message=None):
    enabled = app.config['TELEGRAM']['enabled']
    proxy = app.config['TELEGRAM']['proxy-url']
    token = app.config['TELEGRAM']['proxy-jwt-token']
    timeout = app.config['TELEGRAM']['timeout']

    if not message or not enabled or not proxy or not token:
        return False

    with requests.Session() as s:
        try:
            response = s.post(proxy, timeout=timeout, json={'token': token, 'message': message})
            response.raise_for_status()
        except HTTPError as e:
            data = response.json()
            if data:
                error, message = data.pop('error'), data.pop('message')
                print(f"{error}: {message}", file=sys.stderr)
                return False
            print(f"Request Error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f'An error occurred: {e}', file=sys.stderr)
            return False

    return True

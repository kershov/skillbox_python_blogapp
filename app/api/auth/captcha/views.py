from flask import Blueprint

from app import app
from app.api.auth.captcha.helper import captcha_response
from app.models import CaptchaCode

api_captcha = Blueprint('api_captcha', __name__)


@api_captcha.route('/api/auth/captcha', methods=['GET'])
def get_captcha():
    CaptchaCode.delete_outdated_captchas(app.config['CAPTCHA']['ttl'])

    captcha = CaptchaCode()

    return captcha_response(captcha.save())

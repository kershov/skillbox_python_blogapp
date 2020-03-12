import base64
import io
import random
import string
import uuid

from PIL import Image, ImageDraw, ImageFont
from flask import make_response, jsonify

from app import app


def captcha_response(captcha):
    return make_response(jsonify(captcha.json()), 200)


def generate_captcha_code(code_length=None):
    code_length = code_length or app.config['CAPTCHA']['length']

    symbols = string.ascii_letters + string.digits

    return ''.join(random.choice(symbols) for _ in range(code_length))


def generate_secret_code():
    return str(uuid.uuid4())


def generate_base64_image(code=None, font_size=None):
    if not code or not isinstance(code, str):
        raise ValueError('Code is not set or not a string.')

    font_size = font_size or app.config['CAPTCHA']['font-size']

    image_prefix = "data:image/png;charset=utf-8;base64, "

    font = ImageFont.truetype('times.ttf', font_size)
    image_size = font.getsize(code)

    img = Image.new('RGB', (image_size[0], image_size[1] + 2), color='white')

    draw = ImageDraw.Draw(img)
    draw.text((0, 0), code, font=font, fill=(0, 0, 0))
    del draw

    b = io.BytesIO()
    img.save(b, 'PNG')
    image_bytes = b.getvalue()

    return image_prefix + base64.b64encode(image_bytes).decode()

import os
import string
import random


def create_upload_dir(upload_dir):
    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)


def generate_random_string(length=2):
    symbols = string.ascii_letters + string.digits
    return ''.join(random.choice(symbols) for _ in range(length))

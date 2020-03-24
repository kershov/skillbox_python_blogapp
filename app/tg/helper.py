import re
import threading
from functools import wraps

from app.helper import clear_html_tags


def async_request(f):
    """"
    This runs decorated function in a separate thread
    """
    @wraps(f)
    def run(*args, **kwargs):
        thread = threading.Thread(target=f, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return run


def escape(text):
    """
    Ref: https://core.telegram.org/bots/api#markdownv2-style
    Characters '_‘, ’*‘, ’[‘, ’]‘, ’(‘, ’)‘, ’~‘, ’`‘, ’>‘, ’#‘, ’+‘, ’-‘, ’=‘, ’|‘, ’{‘, ’}‘, ’.‘, ’!‘
    must be escaped with the preceding character ’\'.
    """
    regex, subst = r'[_*\[\]()~`>#+\-=|{}.!]', '\\'
    text = clear_html_tags(text)
    return re.sub(regex, lambda match: subst + match.group(0), text)

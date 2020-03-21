from datetime import datetime

from flask import Blueprint, request

from app.api.calendar.helper import calendar_response

api_calendar = Blueprint('api_calendar', __name__)


@api_calendar.route('/api/calendar', methods=['GET'])
def get_calendar():
    year = request.args.get('year', None, type=int)

    if not year:
        year = datetime.now().year

    return calendar_response(year)

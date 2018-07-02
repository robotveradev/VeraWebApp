import time
from datetime import datetime

from django import template

from interview.forms import ActionInterviewForm

register = template.Library()


@register.filter
def get_interview_form(a=None):
    return ActionInterviewForm


@register.filter
def get_diff(start_date, end_date=None):
    if not end_date:
        end_date = datetime.today()
    d1_ts = time.mktime(start_date.timetuple())
    d2_ts = time.mktime(end_date.timetuple())
    return int(int(d2_ts-d1_ts))


@register.filter
def get_diff_2(end_date, start_date=None):
    if end_date == 1:
        # Hook
        end_date = datetime.today()
    if not start_date:
        start_date = datetime.today()

    d1_ts = time.mktime(start_date.timetuple())
    d2_ts = time.mktime(end_date.timetuple())

    return int(int(d2_ts - d1_ts))


@register.filter
def more_than_equal(f_time, next_time):
    return int(f_time) >= int(next_time)

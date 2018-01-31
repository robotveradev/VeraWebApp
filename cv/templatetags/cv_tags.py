import calendar

from django import template

register = template.Library()


@register.filter(name='month_name')
def month_name(month_number):
    return calendar.month_name[month_number]


@register.filter(name='sub')
def sub(a, b):
    if a < b:
        return 0
    else:
        return a - b

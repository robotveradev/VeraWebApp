from urllib.parse import urlparse

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def icon_for_link(link, size=None):
    parsed = urlparse(link).netloc
    if parsed.startswith('www'):
        parsed = parsed[4:]
    if parsed.startswith('plus'):
        parsed = parsed[5:]
    parsed = get_correct_icon_name(parsed[:parsed.index('.')])
    return mark_safe(
        '<i class="uk-margin-small uk-margin-small-left fa fa-{} fa-{}x" area-hidden="true"></i>'.format(parsed,
                                                                                                         2 if size is
                                                                                                         None
                                                                                                         else size))


def get_correct_icon_name(soc):
    if soc not in settings.SOCIAL_ICONS:
        return soc
    return settings.SOCIAL_ICONS[soc]

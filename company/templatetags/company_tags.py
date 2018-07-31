from urllib.parse import urlparse

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from jobboard.handlers.company import CompanyInterface
from jobboard.handlers.oracle import OracleHandler

register = template.Library()


@register.filter
def icon_for_link(link, size=2):
    parsed = urlparse(link).netloc
    if parsed.startswith('www'):
        parsed = parsed[4:]
    if parsed.startswith('plus'):
        parsed = parsed[5:]
    name = get_correct_icon_name(parsed[:parsed.index('.')])
    return get_icon_for_name(name, size)


def get_correct_icon_name(soc):
    if soc not in settings.SOCIAL_ICONS:
        return soc
    return settings.SOCIAL_ICONS[soc]


@register.filter
def get_icon_for_name(name, size=2):
    return mark_safe(
        '<i class="fa fa-{} fa-{}x blue-text text-lighten-2" area-hidden="true"></i>'.format(name, size))


@register.simple_tag
def member_company_role(member, company):
    if not member.contract_address:
        return None
    ci = CompanyInterface(contract_address=company.contract_address)
    is_owner = ci.is_owner(member.contract_address)
    if is_owner:
        return 'owner'
    is_collaborator = ci.is_collaborator(member.contract_address)
    if is_collaborator:
        return 'collaborator'
    return None


@register.filter
def members_length(address):
    oracle = OracleHandler()
    return oracle.get_company_members_length(address)

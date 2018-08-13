import datetime
import json
import re
from urllib.parse import urlencode

import date_converter
from django import template
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe

from jobboard import blockies
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.oracle import OracleHandler
from jobboard.messages import MESSAGES
from jobboard.models import Transaction
from member_profile.models import Profile
from quiz.models import ActionExam
from vacancy.models import Vacancy, MemberOnVacancy, VacancyOffer

register = template.Library()


@register.filter(name='has_profile')
def has_profile(user_id):
    return Profile.objects.filter(candidate__user_id=user_id).exists()


def get_coin_symbol(id):
    coin_h = CoinHandler()
    return coin_h.symbol


@register.inclusion_tag("jobboard/tags/candidates.html")
def get_candidates(vacancy):
    args = {'vacancy': vacancy, 'profiles': MemberOnVacancy.objects.filter(vacancy=vacancy)}
    return args


@register.filter(name='vacancy_tests_count')
def vacancy_tests_count(vacancy_id):
    return ActionExam.objects.filter(action__pipeline__vacancy_id=vacancy_id).first().questions.count()


@register.inclusion_tag('jobboard/tags/employers.html')
def get_employers(vacancies, candidate_id):
    employers = []
    already = []
    for item in vacancies:
        vac = Vacancy.objects.values('employer__contract_address', 'employer_id').get(pk=item['id'])
        if vac['employer__contract_address'] not in already:
            already.append(vac['employer__contract_address'])
            employers.append({'address': vac['employer__contract_address'],
                              'id': vac['employer_id']})
    return {'employers': employers,
            'candidate_id': candidate_id}


@register.filter(name='is_enabled_vacancy')
def is_enabled_vacancy(vacancy_id):
    vacancy_obj = get_object_or_404(Vacancy, id=vacancy_id)
    return vacancy_obj.enabled


@register.filter
def balance(address):
    coin_h = CoinHandler()
    return coin_h.balanceOf(address) / 10 ** 18


@register.inclusion_tag('jobboard/tags/balances.html')
def get_balance(user):
    if user.contract_address is None:
        return {'balance': None, 'user': user}

    return {'balance': balance(user.contract_address), 'user': user,
            'testnet': settings.NET_URL.startswith('https://rinkeby')}


@register.inclusion_tag('jobboard/tags/allowance.html')
def oracle_allowance(address, user_id):
    if address is None:
        return {'allowance': 0, 'user_id': user_id}
    coin = CoinHandler()
    return {'allowance': coin.allowance(address, settings.VERA_ORACLE_CONTRACT_ADDRESS) / 10 ** 18,
            'user_id': user_id}


@register.filter
def employer_answered(cv_id, vacancy_id):
    return Transaction.objects.filter(txn_type='EmpAnswer', obj_id=cv_id, vac_id=vacancy_id).exists()


def get_vacancy(vac_uuid):
    try:
        return Vacancy.objects.get(uuid=vac_uuid)
    except Vacancy.DoesNotExist:
        return None


@register.inclusion_tag('jobboard/tags/facts.html', takes_context=True)
def facts(context, member):
    date_fields = ['date_from', 'date_up_to', 'date_of_receiving']
    args = {}
    if member.contract_address:
        oracle = OracleHandler()
        fact_keys = oracle.facts_keys(member.contract_address)
        facts_dict = []
        for item in fact_keys:
            fact = oracle.fact(member.contract_address, item)
            f = json.loads(fact[2])
            for date_item in date_fields:
                if date_item in f:
                    f[date_item] = date_converter.string_to_date(f[date_item], current_format='%Y-%m-%dT%H:%M:%S')

            facts_dict.append({'id': item,
                               'from': fact[0],
                               'date': datetime.datetime.fromtimestamp(int(fact[1])),
                               'fact': f})
        args['facts'] = facts_dict
        args['member'] = member
        context.update(args)
    return context


@register.filter
def confirmations(address, f_id):
    oracle = OracleHandler()
    return oracle.member_facts_confirmations_count(address, f_id)


@register.simple_tag
def is_member_verify_fact(sender_address, member_address, fact_id, txns):
    transact_now = False
    for item in txns:
        if item.obj_id == fact_id:
            transact_now = True
    return transact_now or OracleHandler().member_fact_confirmations(sender_address, member_address, fact_id)


@register.filter(name='parse_addresses')
def parse_addresses(string):
    regex = '\\b0x\w+'
    url_template = '<a target="_blank" class="uk-link-muted" href="{}address/{}">{}</a>'
    string = re.sub(regex, url_template.format(settings.NET_URL, '\g<0>', '\g<0>'), string)
    return string


@register.filter(name='paginator_pages')
def paginator_pages(current_page, max_page):
    if max_page < 8:
        return range(2, max_page)
    else:
        if current_page <= 4:
            return range(2, min(7, max_page))
        elif current_page >= max_page - 4:
            return range(max_page - 5, max_page)
        else:
            return range(current_page - 2, current_page + 3)


@register.filter
def need_dots(first, next_o):
    if next_o - first > 1:
        return True
    return False


@register.filter(name='is_owner')
def is_owner(user, current_user):
    return user == current_user


@register.filter(name='can_withdraw')
def can_withdraw(user):
    return not Transaction.objects.values('id').filter(user=user.id, txn_type='Withdraw').exists()


@register.filter(name='get_url_without')
def get_url_without(get_list, item=None):
    url_dict = {}
    for key, value in get_list.items():
        if key == item:
            pass
        else:
            url_dict.update({key: value})
    return urlencode(url_dict)


@register.filter(name='get_blockies_png')
def get_blockies_png(address):
    data = blockies.create(address.lower(), size=8, scale=16)
    return blockies.png_to_data_uri(data)


@register.filter(name='offers_count')
def offers_count(member):
    return VacancyOffer.objects.filter(member=member, is_active=True).count()


@register.simple_tag
def net_url():
    return settings.NET_URL


@register.filter(name='approve_pending')
def approve_pending(user_id):
    return Transaction.objects.filter(user_id=user_id, txn_type='tokenApprove').exists()


@register.inclusion_tag('jobboard/include/candidate_status.html', takes_context=True)
def member_status(context, member, for_change=False):
    oracle = OracleHandler()
    status = oracle.member_status(member.contract_address)
    return {
        'statuses': [{'id': i, 'status': v} for i, v in enumerate(oracle.statuses)],
        'status': status,
        'for_change': for_change,
        'now_pending': context['txns'].filter(txn_type='ChangeStatus').exists()
    }


@register.filter
def get_categories_count(member):
    count = 0
    for item in member.companies.all():
        count += item.quiz_categories.count()
    return count


@register.inclusion_tag('jobboard/tags/blocked_with_tnx.html')
def check_txn(txns, action_type, obj_id):
    b = txns.filter(txn_type=action_type, obj_id=obj_id)
    message = b.exists() and MESSAGES[action_type] or MESSAGES['Not_' + action_type]
    return {
        'message': mark_safe(message)
    }


@register.filter
def txn_message_with_link(txn):
    try:
        message = MESSAGES[txn.txn_type]
    except KeyError:
        message = 'Transaction now pending...'
    link = '<a href="{}" target="_blank" class="vr-link white-text">{}</a>'
    return mark_safe(link.format(net_url() + 'tx/' + txn.txn_hash, message))


@register.filter(name='times')
def times(number):
    return range(number)

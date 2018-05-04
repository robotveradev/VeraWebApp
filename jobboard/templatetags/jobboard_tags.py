import json
import datetime
import re
from django import template
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode
from cv.models import CurriculumVitae
from jobboard import blockies
from jobboard.handlers.new_oracle import OracleHandler
from jobboard.handlers.coin import CoinHandler
from jobboard.models import Candidate, Transaction
from quiz.models import ActionExam
from vacancy.models import Vacancy, CVOnVacancy, VacancyOffer
from django.conf import settings

register = template.Library()


@register.filter(name='has_cv')
def has_cv(user_id):
    return CurriculumVitae.objects.filter(candidate__user_id=user_id).count() > 0


@register.filter(name='allowance_rest')
def allowance_rest(vacancy_id):
    vac = Vacancy.objects.get(id=vacancy_id)
    if not vac.published:
        return 0
    oracle = OracleHandler()
    return oracle.get_vacancy_allowed_rest(vac.uuid) / 10 ** 18


def get_coin_symbol(id):
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    return coin_h.symbol


@register.inclusion_tag("jobboard/tags/candidates.html")
def get_candidates(vacancy):
    args = {'vacancy': vacancy, 'cvs': CVOnVacancy.objects.filter(vacancy=vacancy)}
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


@register.inclusion_tag('jobboard/tags/balances.html')
def get_balance(user, address):
    if address is None:
        return {'balance': None, 'user': user}
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    return {'balance': coin_h.balanceOf(address) / 10 ** 18, 'user': user}


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


@register.inclusion_tag('jobboard/tags/vacancies.html', takes_context=True)
def get_candidate_vacancies(context, candidate):
    vac_set = set()
    oracle = OracleHandler()
    for cv in candidate.cvs.all():
        count = oracle.vacancies_on_cv_length(cv.uuid)
        for i in range(count):
            vac_uuid = oracle.vacancy_on_cv_by_index(cv.uuid, i)
            vac_set.add(vac_uuid)
    vacancies = Vacancy.objects.filter(uuid__in=vac_set)
    return {'vacancies': vacancies,
            'request': context.request,
            'candidate': candidate}


@register.inclusion_tag('jobboard/tags/facts.html')
def get_facts(candidate):
    oracle = OracleHandler()
    fact_keys = oracle.facts_keys(candidate.contract_address)
    args = {}
    facts = []
    for item in fact_keys:
        fact = oracle.fact(candidate.contract_address, item)
        facts.append({'id': item,
                      'from': fact[0],
                      'date': datetime.datetime.fromtimestamp(int(fact[1])),
                      'fact': json.loads(fact[2])})
    args['facts'] = facts
    args['candidate'] = candidate
    return args


def check_fact(f_id):
    return False


@register.filter(name='is_fact_verify')
def is_fact_verify(address, f_id):
    # TODO change for oracle
    return False


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


@register.filter(name='need_dots')
def need_dots(first, next_o):
    # print('first: {}, next: {}'.format(first, next_o))
    # return False
    if next_o - first > 1:
        return True
    return False


@register.filter(name='is_owner')
def is_owner(user, current_user):
    return user == current_user


@register.filter(name='can_withdraw')
def can_withdraw(user):
    return not bool(Transaction.objects.values('id').filter(user=user, txn_type='Withdraw').count())


@register.filter(name='get_url_without')
def get_url_without(get_list, item=None):
    url_dict = {}
    for key, value in get_list.items():
        if key == item:
            pass
        else:
            url_dict.update({key: value})
    return urlencode(url_dict)


@register.filter(name='is_oracle_agent')
def is_oracle_agent(candidate):
    # TODO change this
    oracle = OracleHandler()
    return oracle.is_owner(candidate.contract_address)


@register.filter(name='get_blockies_png')
def get_blockies_png(address):
    data = blockies.create(address.lower(), size=8, scale=16)
    return blockies.png_to_data_uri(data)


@register.filter(name='offers_count')
def offers_count(candidate):
    return VacancyOffer.objects.filter(cv__candidate=candidate, is_active=True).count()


@register.simple_tag
def net_url():
    return settings.NET_URL


@register.filter(name='approve_pending')
def approve_pending(user_id):
    return Transaction.objects.filter(user_id=user_id, txn_type='tokenApprove').exists()

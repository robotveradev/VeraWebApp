import json
import datetime
import re
from django import template
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode
from cv.models import CurriculumVitae
from jobboard import blockies
from jobboard.handlers.candidate import CandidateHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.handlers.coin import CoinHandler
from jobboard.models import Candidate, Employer, Transaction
from quiz.models import VacancyExam
from vacancy.models import Vacancy, CVOnVacancy, VacancyOffer
from django.conf import settings
from jobboard.views import get_relevant

register = template.Library()


@register.filter(name='has_cv')
def has_cv(user_id):
    return CurriculumVitae.objects.filter(candidate__user_id=user_id).count() > 0


@register.filter(name='allowance_rest')
def allowance_rest(vacancy_id):
    vac = Vacancy.objects.values('employer__contract_address', 'contract_address').get(id=vacancy_id)
    if vac['employer__contract_address'] is None or vac['contract_address'] is None:
        return 0
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    return coin_h.allowance(vac['employer__contract_address'],
                            vac['contract_address']) / 10 ** coin_h.decimals


@register.filter(name='get_interview_fee')
def get_interview_fee(vacancy_id):
    vac = Vacancy.objects.values('employer__contract_address', 'contract_address').get(id=vacancy_id)
    if not vac['contract_address']:
        return 0
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    vac_h = VacancyHandler(vac['employer__contract_address'], vac['contract_address'])
    return vac_h.interview_fee() / 10 ** coin_h.decimals


@register.filter(name='get_coin_symbol')
def get_coin_symbol(id):
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    return coin_h.symbol


@register.inclusion_tag("jobboard/tags/candidates.html")
def get_candidates(vacancy):
    args = {}
    args['vacancy'] = vacancy
    args['cvs'] = CVOnVacancy.objects.filter(vacancy=vacancy)
    return args


@register.filter(name='candidate_state')
def candidate_state(vacancy, candidate):
    vac_h = VacancyHandler(settings.WEB_ETH_COINBASE, vacancy.contract_address)
    return vac_h.get_candidate_state(candidate.contract_address)


@register.filter(name='vacancy_tests_count')
def vacancy_tests_count(vacancy_id):
    return VacancyExam.objects.filter(vacancy_id=vacancy_id).first().questions.count()


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


@register.filter(name='is_allowed')
def is_allowed(candidate_id, employer_contract_address):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, candidate.contract_address)
    return can_h.is_agent(employer_contract_address)


@register.filter(name='is_enabled_vacancy')
def is_enabled_vacancy(vacancy_id):
    vacancy_obj = get_object_or_404(Vacancy, id=vacancy_id)
    return vacancy_obj.enabled


@register.inclusion_tag('jobboard/tags/balances.html')
def get_balance(user, address):
    if address is None:
        return {'balance': None, 'user': user}
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    return {'balance': coin_h.balanceOf(address) / 10 ** coin_h.decimals, 'user': user}


@register.filter(name='is_can_subscribe')
def is_can_subscribe(candidate, vacancy):
    if candidate.contract_address is None:
        return False, 'Your contract doesn\'t ready yet'
    if candidate.enabled is False:
        return False, 'You must enable your contract'
    else:
        vac_h = VacancyHandler(settings.WEB_ETH_COINBASE, vacancy.contract_address)
        if vac_h.get_candidate_state(candidate.contract_address) != 'not exist':
            return False, 'You have already subscribed to this vacancy'
        else:
            txn = Transaction.objects.filter(user=candidate.user, txn_type='Subscribe', obj_id=vacancy.id)
            if txn:
                return False, 'You have already send request'
            else:
                return True, ''


@register.filter(name='employer_answered')
def employer_answered(candidate_id, vacancy_id):
    try:
        Transaction.objects.get(txn_type='EmpAnswer', obj_id=candidate_id, vac_id=vacancy_id)
        return True
    except Transaction.DoesNotExist:
        return False


@register.inclusion_tag('jobboard/tags/vacancies.html')
def get_candidate_vacancies(candidate, request):
    vacancies = []
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, candidate.contract_address)
    for item in can_h.get_vacancies():
        try:
            vacancies.append(Vacancy.objects.get(contract_address=item))
        except Vacancy.DoesNotExist:
            pass
    return {'vacancies': vacancies,
            'request': request,
            'candidate': candidate}


@register.inclusion_tag('jobboard/tags/facts.html')
def get_facts(candidate):
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, candidate.contract_address)
    fact_keys = can_h.get_facts()
    args = {}
    facts = []
    for item in fact_keys:
        fact = can_h.get_fact(item)
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
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, address)
    fact = can_h.get_fact(f_id)
    fact_from = fact[0]
    fact_object = json.loads(fact[2])
    return fact_from.casefold() == settings.WEB_ETH_COINBASE.casefold() and fact_object[
        'from'].casefold() == settings.VERA_ORACLE_CONTRACT_ADDRESS.casefold() or check_fact(f_id)


@register.filter(name='can_spend')
def can_spend(vacancy):
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    vac_h = VacancyHandler(settings.WEB_ETH_COINBASE, vacancy.contract_address)
    interview_fee = vac_h.interview_fee()
    employer_balance = coin_h.balanceOf(vacancy.employer.contract_address)
    allowance = coin_h.allowance(vacancy.employer.contract_address, vacancy.contract_address)
    return allowance >= interview_fee and employer_balance >= interview_fee


@register.filter(name='get_wait_candidates_count')
def get_candidates_count(vacancy_address):
    vac_h = VacancyHandler(settings.WEB_ETH_COINBASE, vacancy_address)
    wait_count = accepted_count = revoked_count = paid_count = 0
    for item in vac_h.candidates():
        state = vac_h.get_candidate_state(item)
        if state == 'wait':
            wait_count += 1
        elif state == 'accepted':
            accepted_count += 1
        elif state == 'revoked':
            revoked_count += 1
        elif state == 'paid':
            paid_count += 1
    return {'wait': wait_count,
            'accepted': accepted_count,
            'revoked': revoked_count,
            'paid': paid_count}


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
    if user == current_user:
        return True
    else:
        return False


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
    if not candidate.contract_address:
        return False
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, candidate.contract_address)
    return can_h.is_agent(settings.WEB_ETH_COINBASE)


@register.inclusion_tag('jobboard/include/candidate_relevant.html')
def get_candidate_relevant(candidate):
    vacancies = get_relevant(candidate.user, 3)
    return {'vacancies': vacancies}


@register.filter(name='get_blockies_png')
def get_blockies_png(address):
    data = blockies.create(address.lower(), size=8, scale=16)
    return blockies.png_to_data_uri(data)


@register.filter(name='show_me')
def show_me(a):
    print(a.data)
    return ''


@register.filter(name='offers_count')
def offers_count(candidate):
    return VacancyOffer.objects.filter(cv__candidate=candidate, is_active=True).count()


@register.simple_tag
def net_url():
    return settings.NET_URL

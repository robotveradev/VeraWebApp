import json

import datetime
from django import template
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter

from cv.models import CurriculumVitae
from jobboard.handlers.candidate import CandidateHandler
from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.handlers.coin import CoinHandler
from jobboard.models import Vacancy, Candidate, Employer, VacancyTest, CandidateVacancyPassing, \
    Transaction, CVOnVacancy
from django.conf import settings

register = template.Library()


@register.filter(name='user_role')
def user_role(user_id):
    try:
        Employer.objects.get(user_id=user_id)
        return 'employer'
    except Employer.DoesNotExist:
        try:
            Candidate.objects.get(user_id=user_id)
            return 'candidate'
        except Candidate.DoesNotExist:
            return False


@register.filter(name='has_cv')
def has_cv(user_id):
    if CurriculumVitae.objects.filter(user_id=user_id).count() > 0:
        return True
    else:
        return False


@register.filter(name='allowance_rest')
def allowance_rest(vacancy_id):
    vac = Vacancy.objects.values('employer__contract_address', 'contract_address').get(id=vacancy_id)
    coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    return coin_h.allowance(vac['employer__contract_address'],
                            vac['contract_address']) / 10 ** coin_h.decimals


@register.filter(name='get_interview_fee')
def get_interview_fee(vacancy_id):
    vac = Vacancy.objects.values('employer__contract_address', 'contract_address').get(id=vacancy_id)
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
    return VacancyTest.objects.filter(vacancy_id=vacancy_id, enabled=True).count()


@register.filter(name='is_test_passed')
def is_test_passed(candidate_id, vacancy_test_id):
    try:
        return CandidateVacancyPassing.objects.get(candidate_id=candidate_id, test_id=vacancy_test_id).passed
    except CandidateVacancyPassing.DoesNotExist:
        return None


@register.filter(name='all_test_passed')
def all_test_passed(candidate_id, vacancy_id):
    test_count = VacancyTest.objects.filter(vacancy_id=vacancy_id).count()
    passed = CandidateVacancyPassing.objects.filter(test__vacancy_id=vacancy_id,
                                                    candidate_id=candidate_id)
    is_passed = passed.filter(passed=True).count() == test_count
    finished = passed.exclude(passed=None).count() == test_count
    return is_passed or passed.filter(passed=False).count() == test_count or finished, is_passed


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
    return can_h.is_allowed(employer_contract_address)


@register.filter(name='is_enabled_vacancy')
def is_enabled_vacancy(vacancy_id):
    vacancy_obj = get_object_or_404(Vacancy, id=vacancy_id)
    return vacancy_obj.enabled


@register.inclusion_tag('jobboard/tags/balances.html')
def get_balance(address):
    if address is None:
        return {'balances': None}
    try:
        emp_o = Employer.objects.get(contract_address=address)
        coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
        return {'balances': [{coin_h.symbol: coin_h.balanceOf(emp_o.contract_address) / 10 ** coin_h.decimals}, ]}
    except Employer.DoesNotExist:
        try:
            can_o = Candidate.objects.get(contract_address=address)
            coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
            return {'balances': [{coin_h.symbol: coin_h.balanceOf(can_o.contract_address) / 10 ** coin_h.decimals}, ]}
            # can_h = CandidateHandler(settings.WEB_ETH_COINBASE, can_o.contract_address)
            # can_vac_list = can_h.get_vacancies()
            # balances = []
            # tokens = []
            # for item in can_vac_list:
            #     state = can_h.get_vacancy_state(item)
            #     if state == 'paid':
            #         try:
            #             vac_o = Vacancy.objects.get(contract_address=item)
            #             token = EmployerHandler(settings.WEB_ETH_COINBASE, vac_o.employer.contract_address).token()
            #             if token not in tokens:
            #                 tokens.append(token)
            #                 coin_h = CoinHandler(token)
            #                 balances.append(
            #                     {coin_h.symbol: coin_h.balanceOf(can_o.contract_address) / 10 ** coin_h.decimals})
            #         except Vacancy.DoesNotExist:
            #             pass
            # return {'balances': balances}
        except Candidate.DoesNotExist:
            return None


@register.filter(name='is_can_subscribe')
def is_can_subscribe(candidate, vacancy):
    vac_h = VacancyHandler(settings.WEB_ETH_COINBASE, vacancy.contract_address)
    txn = Transaction.objects.filter(user=candidate.user, txn_type='Subscribe', obj_id=vacancy.id)
    if vac_h.get_candidate_state(candidate.contract_address) == 'not exist' and not txn:
        return True
    else:
        return False


@register.filter(name='employer_answered')
def employer_answered(candidate_id, vacancy_id):
    try:
        Transaction.objects.get(txn_type='EmpAnswer', obj_id=candidate_id, vac_id=vacancy_id)
        return True
    except Transaction.DoesNotExist:
        return False


@register.inclusion_tag('jobboard/tags/vacancies.html')
def get_candidate_vacancies(candidate):
    vacancies = []
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, candidate.contract_address)
    for item in can_h.get_vacancies():
        vacancies.append({'address': item,
                          'state': can_h.get_vacancy_state(item),
                          'id': Vacancy.objects.values('id').get(contract_address=item)['id']})
    return {'vacancies': vacancies}


@register.inclusion_tag('jobboard/tags/facts.html')
def get_facts(candidate):
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, candidate.contract_address)
    fact_keys = can_h.get_facts()
    facts = []
    for item in fact_keys:
        fact = can_h.get_fact(item)
        facts.append({'from': fact[0],
                      'date': datetime.datetime.fromtimestamp(int(fact[1])),
                      'fact': json.loads(fact[2]),
                      'verify': is_fact_verify(candidate.contract_address, item)})
    return {'facts': facts}


def is_fact_verify(address, id):
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, address)
    fact = can_h.get_fact(id)
    return fact[0].lower() == settings.WEB_ETH_COINBASE.lower() or fact[
        0].lower() == settings.VERA_ORACLE_CONTRACT_ADDRESS.lower()

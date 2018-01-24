from django import template
from django.shortcuts import get_object_or_404

from jobboard.handlers.candidate import CandidateHandler
from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.handlers.coin import CoinHandler
from jobboard.models import Vacancy, Candidate, Employer, CurriculumVitae, VacancyTest, CandidateVacancyPassing, \
    Transaction
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
    try:
        CurriculumVitae.objects.get(candidate__user_id=user_id)
        return True
    except CurriculumVitae.DoesNotExist:
        return False


@register.filter(name='allowance_rest')
def allowance_rest(vacancy_id):
    vacancy = Vacancy.objects.get(id=vacancy_id)
    emp_h = EmployerHandler(settings.WEB_ETH_COINBASE, vacancy.employer.contract_address)
    coin_h = CoinHandler(emp_h.token())
    return coin_h.allowance(vacancy.employer.contract_address,
                            vacancy.contract_address) / 10 ** coin_h.decimals


@register.filter(name='get_interview_fee')
def get_interview_fee(vacancy_id):
    vac_o = Vacancy.objects.get(id=vacancy_id)
    emp_h = EmployerHandler(settings.WEB_ETH_COINBASE, vac_o.employer.contract_address)
    coin_h = CoinHandler(emp_h.token())
    vac_h = VacancyHandler(vac_o.employer.contract_address, vac_o.contract_address)
    return vac_h.interview_fee() / 10 ** coin_h.decimals


@register.filter(name='get_coin_symbol')
def get_coin_symbol(employer_id):
    emp_o = Employer.objects.get(id=employer_id)
    employer_handler = EmployerHandler(settings.WEB_ETH_COINBASE, emp_o.contract_address)
    coin_h = CoinHandler(employer_handler.token())
    return coin_h.symbol


@register.inclusion_tag("jobboard/tags/candidates.html")
def get_candidates(vacancy_id):
    args = {}
    args['vacancy'] = Vacancy.objects.get(id=vacancy_id)
    candidates = []
    vacancy_handler = VacancyHandler(settings.WEB_ETH_COINBASE, args['vacancy'].contract_address)
    c_candidates = vacancy_handler.candidates()

    for candidate in c_candidates:
        if vacancy_handler.get_candidate_state(candidate) != 'not exist':
            candidates.append({'state': vacancy_handler.get_candidate_state(candidate),
                               'obj': Candidate.objects.get(contract_address=candidate)})
    args['candidates'] = candidates
    return args


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
        address = Vacancy.objects.values('employer__contract_address', 'employer_id').get(pk=item['id'])
        if address['employer__contract_address'] not in already:
            already.append(address['employer__contract_address'])
            employers.append({'address': address['employer__contract_address'], 'id': address['employer_id']})
    return {'employers': employers, 'candidate_id': candidate_id}


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
        emp_h = EmployerHandler(settings.WEB_ETH_COINBASE, emp_o.contract_address)
        token = emp_h.token()
        coin_h = CoinHandler(token)
        return {'balances': [{coin_h.symbol: coin_h.balanceOf(emp_o.contract_address) / 10 ** coin_h.decimals}, ]}
    except Employer.DoesNotExist:
        try:
            can_o = Candidate.objects.get(contract_address=address)
            can_h = CandidateHandler(settings.WEB_ETH_COINBASE, can_o.contract_address)
            can_vac_list = can_h.get_vacancies()
            balances = []
            tokens = []
            for item in can_vac_list:
                state = can_h.get_vacancy_state(item)
                if state == 'paid':
                    try:
                        vac_o = Vacancy.objects.get(contract_address=item)
                        token = EmployerHandler(settings.WEB_ETH_COINBASE, vac_o.employer.contract_address).token()
                        if token not in tokens:
                            tokens.append(token)
                            coin_h = CoinHandler(token)
                            balances.append(
                                {coin_h.symbol: coin_h.balanceOf(can_o.contract_address) / 10 ** coin_h.decimals})
                    except Vacancy.DoesNotExist:
                        pass
            return {'balances': balances}
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

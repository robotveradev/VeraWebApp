from django import template

from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.handlers.coin import CoinHandler
from jobboard.models import Vacancy, Candidate, Employer, CurriculumVitae
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
    coin_handler = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
    return coin_handler.allowance(vacancy.employer.contract_address,
                                  vacancy.contract_address)


@register.filter(name='get_coin_symbol')
def get_coin_symbol(vacancy_id):
    vacancy = Vacancy.objects.get(id=vacancy_id)
    employer_handler = EmployerHandler(settings.WEB_ETH_COINBASE, vacancy.employer.contract_address)
    veracoin_handler = CoinHandler(employer_handler.token())
    return veracoin_handler.symbol


@register.inclusion_tag("jobboard/tags/candidates.html")
def get_candidates(vacancy_id):
    vacancy = Vacancy.objects.get(id=vacancy_id)
    args = {}
    candidates = []
    vacancy_handler = VacancyHandler(settings.WEB_ETH_COINBASE, vacancy.contract_address)
    c_candidates = vacancy_handler.candidates()

    for candidate in c_candidates:
        if vacancy_handler.get_candidate_state(candidate) != 'not exist':
            candidates.append({'address': candidate,
                               'state': vacancy_handler.get_candidate_state(candidate),
                               'id': Candidate.objects.values('id').get(contract_address=candidate)['id']})
    args['candidates'] = candidates
    return args

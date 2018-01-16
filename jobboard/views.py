from account.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from .handlers.candidate import CandidateHandler
from .models import Vacancy, Employer, Candidate, Specialisation, Keyword, CurriculumVitae
from .decorators import choose_role_required
from .handlers.oracle import OracleHandler
from .handlers.coin import CoinHandler
from web3 import Web3
from django.conf import settings as django_settings


def index(request):
    return render(request, 'jobboard/index.html', {})


@login_required
@choose_role_required(redirect_url='/role/')
def find_job(request):
    args = {}
    args['specializations'] = Specialisation.objects.all()
    args['keywords'] = Keyword.objects.all()
    if request.method == "POST":
        sp = request.POST.getlist('specialization')
        kw = request.POST.getlist('keyword')
        if sp or kw:
            args['vacancies'] = Vacancy.objects.filter(specializations__specialisation__in=sp)
    else:
        args['vacancies'] = Vacancy.objects.all()
    return render(request, 'jobboard/find_job.html', args)


def choose_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        next = request.POST.get('next')
        oracle = OracleHandler(django_settings.WEB_ETH_COINBASE,
                               django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
        if role == 'employer':
            org = request.POST.get('organization')
            inn = request.POST.get('inn')
            token = request.POST.get('token')
            res = oracle.new_employer(Web3.toBytes(hexstr=Web3.sha3(text=org + inn)), token)
            if res:
                emp = Employer()
                emp.user = request.user
                emp.organization = request.POST.get('organization')
                emp.inn = request.POST.get('inn')
                emp.contract_address = res['employer_address']
                emp.save()
        elif role == 'candidate':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            middle_name = request.POST.get('middle_name')
            snails = request.POST.get('snails')
            candidate = Candidate()
            candidate.user = request.user
            candidate.first_name = first_name
            candidate.last_name = last_name
            candidate.middle_name = middle_name
            candidate.snails = snails
            candidate.save()
            res = oracle.new_candidate(
                Web3.toBytes(hexstr=Web3.sha3(text=first_name + middle_name + last_name + snails)))
            candidate.contract_address = res['candidate_address']
            candidate.save()
        if next != '':
            return redirect(next)
        else:
            return redirect(main_page)
    return render(request, 'jobboard/choose_role.html', {'token': django_settings.VERA_COIN_CONTRACT_ADDRESS})


@login_required
@choose_role_required(redirect_url='/role/')
def user_settings(request):
    args = {'role': user_role(request.user.id)}
    coin_contract = CoinHandler(django_settings.VERA_COIN_CONTRACT_ADDRESS)
    if args['role']:
        if args['role'] == 'employer':
            args['employer'] = Employer.objects.get(user_id=request.user.id)
            args['balance'] = coin_contract.balanceOf(args['employer'].contract_address)
            args['symbol'] = coin_contract.symbol
            args['vacancies'] = Vacancy.objects.filter(employer=args['employer'])
        elif args['role'] == 'candidate':
            args['candidate'] = Candidate.objects.get(user_id=request.user.id)
            args['cv'] = CurriculumVitae.objects.filter(candidate=args['candidate'])
            candidate_handler = CandidateHandler(django_settings.VERA_ORACLE_CONTRACT_ADDRESS,
                                                 args['candidate'].contract_address)
            args['vacancies'] = []
            for item in candidate_handler.get_vacancies():
                args['vacancies'].append({'address': item,
                                          'state': candidate_handler.get_vacancy_state(item),
                                          'id': Vacancy.objects.values('id').get(contract_address=item)['id']})
            args['balance'] = coin_contract.balanceOf(args['candidate'].contract_address)
            args['symbol'] = coin_contract.symbol

    return render(request, 'jobboard/settings.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def new_vacancy(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        interview_fee = request.POST.get('interview_fee')
        salary_from = request.POST.get('salary_from')
        salary_to = request.POST.get('salary_to')
        specialisations = request.POST.getlist('specialisation')
        keywords = request.POST.getlist('keywords')
        allowed_amount = request.POST.get('allowed_amount')

        vacancy = Vacancy()
        vacancy.employer = Employer.objects.get(user_id=request.user.id)
        vacancy.title = title
        vacancy.interview_fee = interview_fee
        vacancy.allowed_amount = allowed_amount
        vacancy.salary_from = salary_from
        vacancy.salary_up_to = salary_to
        vacancy.save()
        vacancy.specializations.set(specialisations)
        vacancy.keywords.set(keywords)
        vacancy.save()

        employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE,
                                           vacancy.employer.contract_address)
        res = employer_handler.new_vacancy(int(allowed_amount), int(interview_fee))

        vacancy.contract_address = res['vacancy_address']
        vacancy.save()
        return redirect(user_settings)
    args = {}
    if user_role(request.user.id) == 'candidate':
        args['error'] = True
    else:
        args = {'specializations': Specialisation.objects.all(), 'keywords': Keyword.objects.all()}
    return render(request, 'jobboard/new_vacancy.html', args)


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


def vacancy(request, vacancy_id):
    args = {}
    try:
        args['vacancy'] = Vacancy.objects.get(id=vacancy_id)
        args['role'] = user_role(request.user.id)
        args['may_to_subscribe'] = False
        if args['role'] == 'candidate':
            candidate = Candidate.objects.get(user_id=request.user.id)
            vacancy_handler = VacancyHandler(django_settings.WEB_ETH_COINBASE, args['vacancy'].contract_address)
            candidate_handler = CandidateHandler(django_settings.WEB_ETH_COINBASE, candidate.contract_address)
            c_state = vacancy_handler.get_candidate_state(candidate.contract_address)
            v_state = candidate_handler.get_vacancy_state(args['vacancy'].contract_address)
            if c_state == 'not exist' and v_state == 'not exist':
                args['may_to_subscribe'] = True
        return render(request, 'jobboard/vacancy.html', args)
    except Vacancy.DoesNotExist:
        raise Http404


def subscrabe_to_vacancy(request):
    if request.method == 'POST':
        vacancy_id = request.POST.get('vacancy')
        candidate = Candidate.objects.get(user_id=request.user.id)
        vacancy_obj = get_object_or_404(Vacancy, id=vacancy_id)
        candidate_handler = CandidateHandler(django_settings.WEB_ETH_COINBASE, candidate.contract_address)
        print(candidate_handler.get_vacancy_state(vacancy_obj.contract_address))
        candidate_handler.subscribe_to_interview(vacancy_obj.contract_address)
        return redirect(vacancy, vacancy_id=vacancy_id)


def candidate(request, candidate_id):
    args = {'candidate': get_object_or_404(Candidate, id=candidate_id)}
    candidate_contract_address = args['candidate'].contract_address
    args['employer'] = get_object_or_404(Employer, user_id=request.user.id)
    employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE, args['employer'].contract_address)
    args['vacancies'] = []
    for vacancy in employer_handler.get_vacancies():
        vacancy_handler = VacancyHandler(django_settings.WEB_ETH_COINBASE, vacancy)
        if candidate_contract_address in vacancy_handler.candidates() and vacancy_handler.get_candidate_state(
                candidate_contract_address) != 'not exist':
            args['vacancies'].append({'address': vacancy,
                                      'state': vacancy_handler.get_candidate_state(candidate_contract_address),
                                      'id': Vacancy.objects.values('id').get(contract_address=vacancy)['id']})
    return render(request, 'jobboard/candidate.html', args)


@require_POST
def approve_candidate(request):
    vacancy_id = request.POST.get('vacancy')
    candidate_id = request.POST.get('candidate')
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user)
    candidate_obj = get_object_or_404(Candidate, id=candidate_id)
    employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE, vacancy.employer.contract_address)
    employer_handler.grant_access_to_candidate(vacancy.contract_address, candidate_obj.contract_address)
    return redirect(candidate, candidate_id=candidate_id)


@require_POST
def revoke_candidate(request):
    vacancy_id = request.POST.get('vacancy')
    candidate_id = request.POST.get('candidate')
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user)
    candidate_obj = get_object_or_404(Candidate, id=candidate_id)
    employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE, vacancy.employer.contract_address)
    employer_handler.revoke_access_to_candidate(vacancy.contract_address, candidate_obj.contract_address)
    return redirect(candidate, candidate_id=candidate_id)


def new_cv(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        salary_from = request.POST.get('salary_from')
        specialisations = request.POST.getlist('specialisation')
        keywords = request.POST.getlist('keywords')
        cv = CurriculumVitae()
        cv.candidate = get_object_or_404(Candidate, user_id=request.user.id)
        cv.title = title
        cv.description = description
        cv.salary_from = salary_from
        cv.save()
        cv.specializations.set(specialisations)
        cv.keywords.set(keywords)
        cv.save()
        return redirect(user_settings)
    else:
        args = {}

        if user_role(request.user.id) == 'candidate':
            args = {'specializations': Specialisation.objects.all(), 'keywords': Keyword.objects.all()}
        else:
            args['error'] = True

        return render(request, 'jobboard/new_cv.html', args)

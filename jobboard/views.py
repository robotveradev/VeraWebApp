import re
from account.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from .handlers.candidate import CandidateHandler
from .models import Vacancy, Employer, Candidate, Specialisation, Keyword, CurriculumVitae, VacancyTest, \
    CandidateVacancyPassing, Transaction
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
    args['vacancies'] = Vacancy.objects.filter(enabled=True).exclude(contract_address=None)
    return render(request, 'jobboard/find_job.html', args)


def choose_role(request):
    args = {}
    if request.method == 'POST':
        role = request.POST.get('role')
        next = request.POST.get('next')
        oracle = OracleHandler(django_settings.WEB_ETH_COINBASE,
                               django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
        if role == 'employer':
            org = request.POST.get('organization')
            inn = request.POST.get('inn')
            token = request.POST.get('token')
            try:
                txn_hash = oracle.new_employer(Web3.toBytes(hexstr=Web3.sha3(text=org + inn)), token)
                emp = Employer()
                emp.user = request.user
                emp.organization = request.POST.get('organization')
                emp.inn = request.POST.get('inn')
                emp.save()
                txn = Transaction()
                txn.user = request.user
                txn.txn_hash = txn_hash
                txn.txn_type = 'NewEmployer'
                txn.obj_id = emp.id
                txn.save()
            except ValueError:
                args['error'] = 'Invalid token address'
                return render(request, 'jobboard/choose_role.html', args)
        elif role == 'candidate':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            middle_name = request.POST.get('middle_name')
            snails = request.POST.get('snails')
            txn_hash = oracle.new_candidate(
                Web3.toBytes(hexstr=Web3.sha3(text=first_name + middle_name + last_name + snails)))
            if txn_hash:
                candidate = Candidate()
                candidate.user = request.user
                candidate.first_name = first_name
                candidate.last_name = last_name
                candidate.middle_name = middle_name
                candidate.snails = snails
                candidate.save()
                txn = Transaction()
                txn.user = request.user
                txn.txn_hash = txn_hash
                txn.txn_type = 'NewCandidate'
                txn.obj_id = candidate.id
                txn.save()
        if next != '':
            return redirect(next)
        else:
            return redirect(index)
    args['token'] = django_settings.VERA_COIN_CONTRACT_ADDRESS
    return render(request, 'jobboard/choose_role.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def profile(request):
    args = {}
    args['role'], args['obj'] = user_role(request.user.id)
    if args['role']:
        if args['role'] == 'employer':
            args['vacancies'] = Vacancy.objects.filter(employer=args['obj'])
        elif args['role'] == 'candidate':
            try:
                args['cv'] = CurriculumVitae.objects.get(candidate=args['obj'])
            except CurriculumVitae.DoesNotExist:
                pass
    return render(request, 'jobboard/profile.html', args)


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
        emp_o = Employer.objects.get(user_id=request.user.id)
        emp_h = EmployerHandler(django_settings.WEB_ETH_COINBASE,
                                emp_o.contract_address)
        coin_h = CoinHandler(emp_h.token())
        decimals = coin_h.decimals
        txn_hash = emp_h.new_vacancy(int(allowed_amount) * 10 ** decimals,
                                     int(interview_fee) * 10 ** decimals)
        if txn_hash:
            vac_o = Vacancy()
            vac_o.employer = emp_o
            vac_o.title = title
            vac_o.interview_fee = int(interview_fee) * 10 ** decimals
            vac_o.allowed_amount = int(allowed_amount) * 10 ** decimals
            vac_o.salary_from = salary_from
            vac_o.salary_up_to = salary_to
            vac_o.save()
            vac_o.specializations.set(specialisations)
            vac_o.keywords.set(keywords)
            vac_o.save()
            txn = Transaction()
            txn.user = request.user
            txn.txn_hash = txn_hash
            txn.txn_type = 'NewVacancy'
            txn.obj_id = vac_o.id
            txn.save()
        return redirect(profile)
    args = {}
    if user_role(request.user.id)[0] == 'candidate':
        args['error'] = True
    else:
        args = {'specializations': Specialisation.objects.all(),
                'keywords': Keyword.objects.all(),
                'employer': Employer.objects.get(user_id=request.user.id)}
    return render(request, 'jobboard/new_vacancy.html', args)


def user_role(user_id):
    try:
        return 'employer', Employer.objects.get(user_id=user_id)
    except Employer.DoesNotExist:
        try:
            return 'candidate', Candidate.objects.get(user_id=user_id)
        except Candidate.DoesNotExist:
            return False, None


def vacancy(request, vacancy_id):
    args = {}
    try:
        args['vacancy'] = Vacancy.objects.get(id=vacancy_id)
        args['role'], args['obj'] = user_role(request.user.id)

        return render(request, 'jobboard/vacancy.html', args)
    except Vacancy.DoesNotExist:
        raise Http404


def subscrabe_to_vacancy(request):
    if request.method == 'POST':
        vacancy_id = request.POST.get('vacancy')
        can_o = Candidate.objects.get(user_id=request.user.id)
        vac_o = get_object_or_404(Vacancy, id=vacancy_id)
        if not can_o.contract_address or not vac_o.contract_address:
            raise Http404
        candidate_handler = CandidateHandler(django_settings.WEB_ETH_COINBASE, can_o.contract_address)
        txn_hash = candidate_handler.subscribe_to_interview(vac_o.contract_address)
        txn = Transaction()
        txn.txn_hash = txn_hash
        txn.txn_type = 'Subscribe'
        txn.obj_id = vac_o.id
        txn.user = request.user
        txn.save()
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
    vac_o = get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user)
    can_o = get_object_or_404(Candidate, id=candidate_id)
    employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE, vac_o.employer.contract_address)
    txn_hash = employer_handler.grant_access_to_candidate(vac_o.contract_address, can_o.contract_address)
    txn = Transaction()
    txn.txn_hash = txn_hash
    txn.user = request.user
    txn.txn_type = 'EmpAnswer'
    txn.obj_id = candidate_id
    txn.vac_id = vacancy_id
    txn.save()
    return redirect(vacancy, vacancy_id=vacancy_id)


@require_POST
def revoke_candidate(request):
    vacancy_id = request.POST.get('vacancy')
    candidate_id = request.POST.get('candidate')
    vac_o = get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user)
    can_o = get_object_or_404(Candidate, id=candidate_id)
    employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE, vac_o.employer.contract_address)
    txn_hash = employer_handler.revoke_access_to_candidate(vac_o.contract_address, can_o.contract_address)
    txn = Transaction()
    txn.txn_hash = txn_hash
    txn.user = request.user
    txn.txn_type = 'EmpAnswer'
    txn.obj_id = candidate_id
    txn.vac_id = vacancy_id
    txn.save()
    return redirect(vacancy, vacancy_id=vacancy_id)


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
        return redirect(profile)
    else:
        args = {}

        if user_role(request.user.id)[0] == 'candidate':
            args = {'specializations': Specialisation.objects.all(), 'keywords': Keyword.objects.all()}
        else:
            args['error'] = True

        return render(request, 'jobboard/new_cv.html', args)


def vacancy_tests(request, vacancy_id):
    args = {'vacancy': get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user),
            'tests': VacancyTest.objects.filter(vacancy_id=vacancy_id)}
    return render(request, 'jobboard/vacancy_tests.html', args)


def vacancy_test_new(request, vacancy_id):
    args = {'vacancy': get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user)}
    return render(request, 'jobboard/new_test.html', args)


@require_POST
def new_test(request):
    if request.method == "POST":
        vacancy_id = request.POST.get('vacancy')
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        max_attempts = request.POST.get('max_attempts')
        title = request.POST.get('title')

        test = VacancyTest()
        test.question = question
        test.answer = answer
        test.title = title
        test.vacancy_id = vacancy_id
        if max_attempts == '' or int(max_attempts) < 1:
            test.save()
        else:
            test.max_attempts = max_attempts
            test.save()
        return redirect(vacancy_tests, vacancy_id=vacancy_id)


def candidate_testing(request, vacancy_id):
    vacancy_obj = get_object_or_404(Vacancy, id=vacancy_id)
    candidate_obj = get_object_or_404(Candidate, user=request.user)
    if request.method == 'POST':
        for item in request.POST.keys():
            match = re.match(r'answer_([0-9]+)', item)
            if match:
                test_id = match.group(1)
                test_obj = get_object_or_404(VacancyTest, id=test_id)
                cvp, created = CandidateVacancyPassing.objects.get_or_create(candidate=candidate_obj,
                                                                             test_id=test_id)
                if request.POST.get(item).lower() == test_obj.answer.lower():
                    if created:
                        cvp.passed = True
                    else:
                        cvp.passed = (cvp.attempts + 1 <= test_obj.max_attempts)
                else:
                    if not created:
                        cvp.attempts += 1
                    if cvp.attempts >= test_obj.max_attempts:
                        cvp.passed = False
                cvp.save()
    vacancy_handler = VacancyHandler(django_settings.WEB_ETH_COINBASE, vacancy_obj.contract_address)
    state = vacancy_handler.get_candidate_state(candidate_obj.contract_address)
    if state != 'accepted':
        raise Http404
    else:
        args = {'vacancy': vacancy_obj,
                'candidate': candidate_obj,
                'tests': VacancyTest.objects.values('id', 'title', 'question').filter(vacancy=vacancy_obj,
                                                                                      enabled=True)}
        return render(request, 'jobboard/candidate_testing.html', args)


def pay_to_candidate(request, vacancy_id):
    candidate_obj = get_object_or_404(Candidate, user=request.user)
    vacancy_obj = get_object_or_404(Vacancy, id=vacancy_id)
    test_count = VacancyTest.objects.filter(vacancy_id=vacancy_id).count()
    passed_count = CandidateVacancyPassing.objects.filter(test__vacancy_id=vacancy_id,
                                                          candidate_id=candidate_obj.id,
                                                          passed=True).count()
    if passed_count >= test_count:
        passed = True
    else:
        passed = False
    vacancy_handler = VacancyHandler(django_settings.WEB_ETH_COINBASE, vacancy_obj.contract_address)
    state = vacancy_handler.get_candidate_state(candidate_obj.contract_address)
    if state != 'accepted' or not passed:
        return HttpResponse('I see the cheater here', status=404)
    else:
        employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE, vacancy_obj.employer.contract_address)
        employer_handler.pay_to_candidate(vacancy_obj.contract_address, candidate_obj.contract_address)
        return HttpResponse('ok', status=200)


def employer_about(request, employer_id):
    args = {}
    args['employer'] = get_object_or_404(Employer, id=employer_id)
    args['vacancies'] = Vacancy.objects.filter(employer_id=employer_id)
    return render(request, 'jobboard/employer_about.html', args)

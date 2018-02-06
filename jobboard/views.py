import re

import time
from account.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from cv.models import CurriculumVitae
from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.tasks import save_txn_to_history
from .handlers.candidate import CandidateHandler
from .models import Vacancy, Employer, Candidate, Specialisation, Keyword, VacancyTest, \
    CandidateVacancyPassing, Transaction, CVOnVacancy, TransactionHistory
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
    args['vacancies'] = Vacancy.objects.filter(enabled=True, employer__enabled=True).exclude(contract_address=None)
    return render(request, 'jobboard/find_job.html', args)


def choose_role(request):
    args = {}
    if request.method == 'POST':
        role = request.POST.get('role')
        next = request.POST.get('next')
        oracle = OracleHandler(django_settings.WEB_ETH_COINBASE,
                               django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
        tax_number = request.POST.get('tax_number')
        if role == 'employer':
            org = request.POST.get('organization')
            try:
                txn_hash = oracle.new_employer(Web3.toBytes(hexstr=Web3.sha3(text=org + tax_number)),
                                               django_settings.VERA_COIN_CONTRACT_ADDRESS)
            except ValueError:
                args['error'] = 'Invalid token address'
                return render(request, 'jobboard/choose_role.html', args)
            else:
                save_txn_to_history.delay(request.user.id, txn_hash, 'Creation of a new employer contract')
                emp = Employer()
                emp.user = request.user
                emp.organization = request.POST.get('organization')
                emp.tax_number = request.POST.get('tax_number')
                emp.save()
                txn = Transaction()
                txn.user = request.user
                txn.txn_hash = txn_hash
                txn.txn_type = 'NewEmployer'
                txn.obj_id = emp.id
                txn.save()
        elif role == 'candidate':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            middle_name = request.POST.get('middle_name')
            txn_hash = oracle.new_candidate(
                Web3.toBytes(hexstr=Web3.sha3(text=first_name + middle_name + last_name + tax_number)))
            if txn_hash:
                save_txn_to_history.delay(request.user.id, txn_hash, 'Creation of a new candidate contract')
                can_o = Candidate()
                can_o.user = request.user
                can_o.first_name = first_name
                can_o.last_name = last_name
                can_o.middle_name = middle_name
                can_o.tax_number = tax_number
                can_o.save()
                txn = Transaction()
                txn.user = request.user
                txn.txn_hash = txn_hash
                txn.txn_type = 'NewCandidate'
                txn.obj_id = can_o.id
                txn.save()
        if next != '':
            return redirect(next)
        else:
            return redirect(profile)
    return render(request, 'jobboard/choose_role.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def profile(request, active_cv=None):
    args = {}
    args['role'], args['obj'] = user_role(request.user.id)
    if args['role']:
        if args['role'] == 'employer':
            args['vacancies'] = Vacancy.objects.filter(employer=args['obj'])
        elif args['role'] == 'candidate':
            args['active'] = active_cv
            args['cv'] = CurriculumVitae.objects.filter(candidate=args['obj'])
    return render(request, 'jobboard/profile.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def new_vacancy(request):
    args = {}
    if user_role(request.user.id)[0] == 'candidate':
        args['error'] = 'Candidate cannot place a vacancy'
    else:
        if request.method == 'POST':
            title = request.POST.get('title')
            interview_fee = request.POST.get('interview_fee')
            salary_from = request.POST.get('salary_from')
            salary_to = request.POST.get('salary_to')
            specialisations = request.POST.getlist('specialisation')
            keywords = request.POST.getlist('keywords')
            allowed_amount = request.POST.get('allowed_amount')
            emp_o = Employer.objects.get(user_id=request.user.id)
            coin_h = CoinHandler(django_settings.VERA_COIN_CONTRACT_ADDRESS)
            oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
            decimals = coin_h.decimals
            user_balance = coin_h.balanceOf(emp_o.contract_address) // 10 ** decimals
            if user_balance < oracle.vacancy_fee // 10 ** decimals:
                args['error'] = 'The cost of placing a vacancy of {} tokens. Your balance {} tokens'.format(
                    oracle.vacancy_fee / 10 ** decimals,
                    user_balance)
            else:
                txn_hash = oracle.new_vacancy(emp_o.contract_address,
                                              int(allowed_amount) * 10 ** decimals,
                                              int(interview_fee) * 10 ** decimals)
                if txn_hash:
                    save_txn_to_history.delay(request.user.id, txn_hash, 'Creation of a new vacancy: {}'.format(title))
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
        args['specializations'] = Specialisation.objects.all()
        args['keywords'] = Keyword.objects.all()
        args['employer'] = Employer.objects.get(user_id=request.user.id)
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
        if args['role'] == 'candidate':
            args['cv'] = CurriculumVitae.objects.filter(candidate=args['obj'], published=True)
        return render(request, 'jobboard/vacancy.html', args)
    except Vacancy.DoesNotExist:
        raise Http404


@login_required
def subscribe_to_vacancy(request, vacancy_id, cv_id):
    can_o = get_object_or_404(Candidate, user_id=request.user.id)
    vac_o = get_object_or_404(Vacancy, id=vacancy_id)
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate=can_o)

    if not can_o.contract_address or not vac_o.contract_address:
        raise Http404

    oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
    oracle.unlockAccount()
    can_h = CandidateHandler(django_settings.WEB_ETH_COINBASE, can_o.contract_address)
    txn_hash = can_h.subscribe_to_interview(vac_o.contract_address)

    cvonvac = CVOnVacancy()
    cvonvac.cv = cv_o
    cvonvac.vacancy = vac_o
    cvonvac.save()

    txn = Transaction()
    txn.txn_hash = txn_hash
    txn.txn_type = 'Subscribe'
    txn.obj_id = vac_o.id
    txn.user = request.user
    txn.save()

    save_txn_to_history.delay(request.user.id, txn_hash, 'Subscribe to vacancy {}'.format(vac_o.title))
    return redirect(vacancy, vacancy_id=vacancy_id)


@login_required
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
    oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
    oracle.unlockAccount()
    txn_hash = employer_handler.grant_access_to_candidate(vac_o.contract_address, can_o.contract_address)
    txn = Transaction()
    txn.txn_hash = txn_hash
    txn.user = request.user
    txn.txn_type = 'EmpAnswer'
    txn.obj_id = candidate_id
    txn.vac_id = vacancy_id
    txn.save()
    save_txn_to_history.delay(request.user.id, txn_hash,
                              'Candidate {} approved to vacancy {}'.format(can_o.contract_address,
                                                                           vac_o.contract_address))
    save_txn_to_history.delay(can_o.user_id, txn_hash,
                              'Employer {} approve your candidacy to vacancy {}'.format(vac_o.employer.contract_address,
                                                                                        vac_o.contract_address))
    return redirect(vacancy, vacancy_id=vacancy_id)


@require_POST
def revoke_candidate(request):
    vacancy_id = request.POST.get('vacancy')
    candidate_id = request.POST.get('candidate')
    vac_o = get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user)
    can_o = get_object_or_404(Candidate, id=candidate_id)
    employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE, vac_o.employer.contract_address)
    oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
    oracle.unlockAccount()
    txn_hash = employer_handler.revoke_access_to_candidate(vac_o.contract_address, can_o.contract_address)
    txn = Transaction()
    txn.txn_hash = txn_hash
    txn.user = request.user
    txn.txn_type = 'EmpAnswer'
    txn.obj_id = candidate_id
    txn.vac_id = vacancy_id
    txn.save()
    save_txn_to_history.delay(request.user.id, txn_hash,
                              'Candidate {} revoked to vacancy {}'.format(can_o.contract_address,
                                                                          vac_o.contract_address))
    save_txn_to_history.delay(can_o.user_id, txn_hash,
                              'Employer {} revoke your candidacy to vacancy {}'.format(vac_o.employer.contract_address,
                                                                                       vac_o.contract_address))
    return redirect(vacancy, vacancy_id=vacancy_id)


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
    can_o = get_object_or_404(Candidate, user=request.user)
    vac_o = get_object_or_404(Vacancy, id=vacancy_id)
    test_count = VacancyTest.objects.filter(vacancy_id=vacancy_id).count()
    passed_count = CandidateVacancyPassing.objects.filter(test__vacancy_id=vacancy_id,
                                                          candidate_id=can_o.id,
                                                          passed=True).count()
    if passed_count >= test_count:
        passed = True
    else:
        passed = False
    vacancy_handler = VacancyHandler(django_settings.WEB_ETH_COINBASE, vac_o.contract_address)
    state = vacancy_handler.get_candidate_state(can_o.contract_address)
    if state != 'accepted' or not passed:
        return HttpResponse('I see the cheater here', status=404)
    else:
        oracle_h = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)

        txn_hash = oracle_h.pay_to_candidate(vac_o.employer.contract_address,
                                             can_o.contract_address,
                                             vac_o.contract_address)
        save_txn_to_history.delay(vac_o.employer.user_id, txn_hash,
                                  'Pay to candidate {} from vacancy {}'.format(can_o.contract_address,
                                                                               vac_o.contract_address))
        save_txn_to_history.delay(can_o.user_id, txn_hash,
                                  'Pay interview fee from vacancy {}'.format(vac_o.contract_address))
        can_h = CandidateHandler(django_settings.WEB_ETH_COINBASE,
                                 can_o.contract_address)
        fact = {'title': 'Test for vacancy "{}" passed.'.format(vac_o.title),
                'date': time.time(),
                'employer': vac_o.employer.organization}
        fact_txn_hash = can_h.new_fact(fact)
        save_txn_to_history.delay(can_o.user_id, fact_txn_hash, 'New fact from {}'.format(vac_o.employer.organization))
        return redirect(profile)


def employer_about(request, employer_id):
    args = {}
    args['employer'] = get_object_or_404(Employer, id=employer_id)
    args['vacancies'] = Vacancy.objects.filter(employer_id=employer_id)
    return render(request, 'jobboard/employer_about.html', args)


def user_help(request):
    return render(request, 'jobboard/user_help.html', {})


def change_contract_status(request):
    role, obj = user_role(request.user.id)
    if role:
        oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)

        if obj.enabled:
            txn_hash = oracle.pause_contract(obj.contract_address)
        elif obj.enabled is False:
            txn_hash = oracle.unpause_contract(obj.contract_address)
        else:
            txn_hash = False

        if txn_hash:
            obj.enabled = None
            obj.save()
            txn = Transaction()
            txn.user = request.user
            txn.txn_hash = txn_hash
            txn.txn_type = role + 'Change'
            txn.obj_id = obj.id
            txn.save()
            save_txn_to_history.delay(obj.user_id, txn_hash,
                                      '{} change contract {} status'.format(role.capitalize(), obj.contract_address))
    return redirect(profile)


def change_vacancy_status(request, vacancy_id):
    vac_o = get_object_or_404(Vacancy, employer__user=request.user, id=vacancy_id)
    emp_h = EmployerHandler(django_settings.WEB_ETH_COINBASE, vac_o.employer.contract_address)
    oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
    oracle.unlockAccount()
    if vac_o.enabled is True:
        txn_hash = emp_h.pause_vacancy(vac_o.contract_address)
    elif vac_o.enabled is False:
        txn_hash = emp_h.unpause_vacancy(vac_o.contract_address)
    else:
        txn_hash = False

    if txn_hash:
        vac_o.enabled = None
        vac_o.save()
        txn = Transaction()
        txn.txn_hash = txn_hash
        txn.user = request.user
        txn.txn_type = 'vacancyChange'
        txn.obj_id = vac_o.id
        txn.save()
        save_txn_to_history.delay(request.user.id, txn_hash, 'Change vacancy {} status'.format(vac_o.contract_address))
    return redirect(profile)

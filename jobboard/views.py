import json
import re
import time
from django.utils import timezone
from account.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from web3.utils.validation import validate_address
from cv.models import CurriculumVitae, Busyness, Schedule
from jobboard.forms import LearningForm, WorkedForm, CertificateForm
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.tasks import save_txn_to_history, save_txn
from .handlers.candidate import CandidateHandler
from .models import Employer, Candidate, Specialisation, Keyword, TransactionHistory
from vacancy.models import Vacancy, VacancyTest, CandidateVacancyPassing
from .decorators import choose_role_required
from .handlers.oracle import OracleHandler
from web3 import Web3
from django.conf import settings as django_settings
from django.db.models import Q


def index(request):
    return render(request, 'jobboard/index.html', {})


@login_required
@choose_role_required(redirect_url='/role/')
def find_job(request):
    periods = [{'id': 1, 'days': 30, 'title': 'for month', 'type': 'period'},
               {'id': 2, 'days': 7, 'title': 'for week', 'type': 'period'},
               {'id': 3, 'days': 3, 'title': 'for three days', 'type': 'period'},
               {'id': 4, 'days': 1, 'title': 'for day', 'type': 'period'}]
    sorts = [{'id': 1, 'order': '-salary_from', 'title': 'by salary descending', 'type': 'sort'},
             {'id': 2, 'order': 'salary_from', 'title': 'by salary ascending', 'type': 'sort'},
             {'id': 3, 'order': '-created_at', 'title': 'by date', 'type': 'sort'}]
    if 'filter' in request.GET:
        vacancies = Vacancy.objects.filter(enabled=True, employer__enabled=True).exclude(contract_address=None)
    else:
        vacancies = get_relevant(request.user)

    if 'period' in request.GET:
        period = get_item(periods, int(request.GET.get('period')))
        if not period:
            period = periods[0]
    else:
        period = periods[0]
    vacancies = vacancies.filter(created_at__gte=timezone.now() - timezone.timedelta(days=period['days']))

    if 'sort' in request.GET:
        sort_by = get_item(sorts, int(request.GET.get('sort')))
        if not sort_by:
            sort_by = sorts[2]
    else:
        sort_by = sorts[2]
    vacancies = vacancies.order_by(sort_by['order'])

    specializations = Specialisation.objects.all()
    keywords = Keyword.objects.all()
    busyness = Busyness.objects.all()
    schedule = Schedule.objects.all()
    args = {'salary_range': [1000, 2000, 3000, 4000, 5000, 6000, 7000, ]}
    if 'specialisation' in request.GET:
        args['selected_spec'] = Specialisation.objects.filter(pk=request.GET.get('specialisation')).first()
        vacancies = vacancies.filter(specializations__in=[request.GET.get('specialisation'), ])
        specializations = Specialisation.objects.filter(parent_specialisation=request.GET.get('specialisation'))
    if 'keyword' in request.GET:
        args['selected_keyword'] = Keyword.objects.filter(pk=request.GET.get('keyword')).first()
        vacancies = vacancies.filter(keywords__in=[request.GET.get('keyword'), ])
        keywords = keywords.exclude(id=request.GET['keyword'])
    if 'salary' in request.GET:
        args['selected_salary'] = request.GET.get('salary')
        vacancies = vacancies.filter(salary_from__gte=args["selected_salary"])
        args['salary_range'] = []
    if 'busyness' in request.GET:
        args['selected_busyness'] = Busyness.objects.filter(pk=request.GET.get('busyness')).first()
        vacancies = vacancies.filter(busyness__in=[request.GET.get('busyness'), ])
        busyness = busyness.exclude(id=request.GET.get('busyness'))
    if 'schedule' in request.GET:
        args['selected_schedule'] = Schedule.objects.filter(pk=request.GET.get('schedule')).first()
        vacancies = vacancies.filter(schedule__in=[request.GET.get('schedule'), ])
        schedule = schedule.exclude(id=request.GET.get('schedule'))
    paginator = Paginator(vacancies, request.GET.get('list') or 25)
    page = request.GET.get('page')
    args['specializations'] = specializations
    args['keywords'] = keywords
    args['vacancies'] = paginator.get_page(page)
    args['vacancies_all'] = vacancies
    args['busyness'] = busyness
    args['schedule'] = schedule
    args['periods'] = periods
    args['selected_period'] = period
    args['sorts'] = sorts
    args['selected_sort'] = sort_by
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

                save_txn.delay(txn_hash, 'NewEmployer', request.user.id, emp.id)
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

                save_txn.delay(txn_hash, 'NewCandidate', request.user.id, can_o.id)
        if next != '':
            return redirect(next)
        else:
            return redirect(profile)
    return render(request, 'jobboard/choose_role.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def profile(request):
    args = {}
    args['role'], args['obj'] = user_role(request.user.id)
    if args['role']:
        if args['role'] == 'employer':
            vacancies = Vacancy.objects.filter(employer=args['obj'])
            args['vacancies'] = vacancies.order_by('-created_at')[:3]
            args['vacancies_count'] = vacancies.count()
        if args['role'] == 'candidate':
            args['learning_form'] = LearningForm()
            args['worked_form'] = WorkedForm()
            args['certificate_form'] = CertificateForm()
            args['cv'] = CurriculumVitae.objects.filter(candidate=args['obj'])
    return render(request, 'jobboard/profile.html', args)


def user_role(user_id):
    try:
        return 'employer', Employer.objects.get(user_id=user_id)
    except Employer.DoesNotExist:
        try:
            return 'candidate', Candidate.objects.get(user_id=user_id)
        except Candidate.DoesNotExist:
            return False, None


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

    save_txn.delay(txn_hash, 'EmpAnswer', request.user.id, candidate_id, vacancy_id)

    save_txn_to_history.delay(request.user.id, txn_hash,
                              'Candidate {} approved to vacancy {}'.format(can_o.contract_address,
                                                                           vac_o.contract_address))
    save_txn_to_history.delay(can_o.user_id, txn_hash,
                              'Employer {} approve your candidacy to vacancy {}'.format(vac_o.employer.contract_address,
                                                                                        vac_o.contract_address))
    return redirect('vacancy', vacancy_id=vacancy_id)


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

    save_txn.delay(txn_hash, 'EmpAnswer', request.user.id, candidate_id, vacancy_id)

    save_txn_to_history.delay(request.user.id, txn_hash,
                              'Candidate {} revoked to vacancy {}'.format(can_o.contract_address,
                                                                          vac_o.contract_address))
    save_txn_to_history.delay(can_o.user_id, txn_hash,
                              'Employer {} revoke your candidacy to vacancy {}'.format(vac_o.employer.contract_address,
                                                                                       vac_o.contract_address))
    return redirect('vacancy', vacancy_id=vacancy_id)


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
                        # todo: revoke candidate когда завалил тесты
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
        fact = {'from': django_settings.VERA_ORACLE_CONTRACT_ADDRESS,
                'type': 'vac_pass',
                'title': 'Test for vacancy "{}" passed.'.format(vac_o.title),
                'date': time.time(),
                'employer': vac_o.employer.organization}
        fact_txn_hash = can_h.new_fact(fact)
        save_txn_to_history.delay(can_o.user_id, fact_txn_hash, 'New fact from {}'.format(vac_o.employer.organization))
        return redirect(profile)


def employer_about(request, employer_id):
    args = {}
    args['employer'] = get_object_or_404(Employer, id=employer_id)
    if args['employer'].user == request.user:
        return redirect(profile)
    args['vacancies'] = Vacancy.objects.filter(employer_id=employer_id, enabled=True)
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
            save_txn.delay(txn_hash, role + 'Change', request.user.id, obj.id)
            save_txn_to_history.delay(obj.user_id, txn_hash,
                                      '{} change contract {} status'.format(role.capitalize(), obj.contract_address))
    return redirect(profile)


def transactions(request):
    args = {'net_url': django_settings.NET_URL}
    all_txns = TransactionHistory.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(all_txns, request.GET.get('list') or 25)
    page = request.GET.get('page')
    args['txns'] = paginator.get_page(page)
    return render(request, 'jobboard/transactions.html', args)


#
# @require_POST
# def increase_vacancy_allowance(request):
#     allowance = request.POST.get('allowance')
#     vac_o = get_object_or_404(Vacancy, id=request.POST.get('vac_id'), employer__user=request.user)
#     coin_h = CoinHandler(django_settings.VERA_COIN_CONTRACT_ADDRESS, vac_o.employer.contract_address)
#     old_allowance = coin_h.allowance(vac_o.employer.contract_address, vac_o.contract_address)
#     coin_h.approve(vac_o.contract_address, 0)
#     txh_hash = coin_h.approve(vac_o.contract_address, int(allowance) + int(old_allowance))
#     return HttpResponse(txh_hash, status=200)

def get_item(periods, f_id):
    for item in periods:
        if item['id'] == f_id:
            return item
    return False


def get_relevant(user, limit=None):
    role, obj = user_role(user.id)
    if role == 'employer':
        return Vacancy.objects.filter(employer=obj)
    elif role == 'candidate':
        cvs = CurriculumVitae.objects.filter(candidate=obj, published=True)
        specs_list = list(set([item['specialisations__id'] for item in cvs.values('specialisations__id') if
                               item['specialisations__id'] is not None]))
        keywords_list = list(
            set([item['keywords__id'] for item in cvs.values('keywords__id') if item['keywords__id'] is not None]))
        vacs = Vacancy.objects.filter(Q(enabled=True),
                                      Q(employer__enabled=True),
                                      Q(specializations__in=specs_list) |
                                      Q(keywords__in=keywords_list)).exclude(
            contract_address=None).distinct()
        return vacs[:limit] if limit else vacs


@login_required
@choose_role_required(redirect_url='/role/')
def withdraw(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        amount = request.POST.get('amount')
        _, obj = user_role(request.user)
        if obj.contract_address is None:
            return redirect(profile)
        try:
            validate_address(address)
        except ValueError:
            return HttpResponse('Invalid address')
        else:
            oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
            coin_h = CoinHandler(django_settings.VERA_COIN_CONTRACT_ADDRESS)
            user_balance = coin_h.balanceOf(obj.contract_address)
            if int(float(amount) * 10 ** 18) > user_balance:
                return HttpResponse('You do not have so many coins', status=200)
            else:
                txn_hash = oracle.withdraw(obj.contract_address, address, int(float(amount) * 10 ** 18))
                save_txn_to_history.delay(obj.user_id, txn_hash,
                                          'Withdraw {} Vera token from {} to {}'.format(amount,
                                                                                        obj.contract_address,
                                                                                        address))
                save_txn.delay(txn_hash, 'Withdraw', request.user.id, obj.id)
    return redirect(profile)


@login_required
@choose_role_required(redirect_url='/role/')
def check_agent(request):
    if request.is_ajax():
        if request.method == 'POST':
            agent_address = request.POST.get('agent_address')
            try:
                validate_address(agent_address)
            except ValueError:
                return HttpResponse('Invalid address', status=400)
            else:
                role, obj = user_role(request.user.id)
                emp_h = EmployerHandler(django_settings.WEB_ETH_COINBASE, obj.contract_address)
                if agent_address.casefold() == django_settings.WEB_ETH_COINBASE.casefold():
                    return HttpResponse('oracle', status=200)
                return HttpResponse(emp_h.is_agent(agent_address), status=200)
        else:
            return HttpResponse('You must use Post request', status=400)


@login_required
@choose_role_required(redirect_url='/role/')
def grant_agent(request):
    _, obj = user_role(request.user.id)
    grant_address = request.GET.get('address')
    if grant_address == django_settings.WEB_ETH_COINBASE:
        return redirect(profile)
    if grant_address is not None:
        oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
        txn_hash = oracle.grant_agent(obj.contract_address, grant_address)
        save_txn_to_history.delay(request.user.id, txn_hash, 'Grant access for agent {}'.format(grant_address))
    return redirect(profile)


@login_required
@choose_role_required(redirect_url='/role/')
def revoke_agent(request):
    _, obj = user_role(request.user.id)
    revoke_address = request.GET.get('address')
    if revoke_address == django_settings.WEB_ETH_COINBASE:
        return redirect(profile)
    if revoke_address is not None:
        oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
        txn_hash = oracle.revoke_agent(obj.contract_address, revoke_address)
        save_txn_to_history.delay(request.user.id, txn_hash, 'Revoke access for agent {}'.format(revoke_address))
    return redirect(profile)


@login_required
@choose_role_required(redirect_url='/role/')
def new_fact(request):
    if request.method == 'POST':
        f_type = request.POST.get('f_type')
        _, obj = user_role(request.user.id)
        if f_type == 'learning':
            form = LearningForm(request.POST)
        elif f_type == 'worked':
            form = WorkedForm(request.POST)
        elif f_type == 'certification':
            form = CertificateForm(request.POST)
        if form and form.is_valid():
            fact = form.cleaned_data
            fact.update({'type': f_type, 'from': obj.contract_address})
            can_h = CandidateHandler(django_settings.WEB_ETH_COINBASE, obj.contract_address)
            oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
            oracle.unlockAccount()
            txn_hash = can_h.new_fact(fact)
            save_txn_to_history.delay(obj.user_id, txn_hash, 'New "{}" fact added'.format(f_type))
    return redirect(profile)

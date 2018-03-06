from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, RedirectView

from cv.models import CurriculumVitae
from jobboard.decorators import choose_role_required
from jobboard.handlers.candidate import CandidateHandler
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Candidate
from django.conf import settings as django_settings

from vacancy.forms import VacancyForm, EditVacancyForm
from vacancy.models import Vacancy, CVOnVacancy, VacancyTest, VacancyOffer
from jobboard.tasks import save_txn_to_history, save_txn

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'


@login_required
@choose_role_required(redirect_url='/role/')
def new_vacancy(request):
    args = {}
    form = VacancyForm()
    args['role'], args['obj'] = request.role, request.role_object
    if request.method == 'POST' and args['role'] == 'employer':
        coin_h = CoinHandler(django_settings.VERA_COIN_CONTRACT_ADDRESS)
        oracle = OracleHandler(django_settings.WEB_ETH_COINBASE, django_settings.VERA_ORACLE_CONTRACT_ADDRESS)
        decimals = coin_h.decimals
        user_balance = coin_h.balanceOf(args['obj'].contract_address) // 10 ** decimals
        if user_balance < oracle.vacancy_fee // 10 ** decimals:
            args['error'] = 'The cost of placing a vacancy of {} tokens. Your balance {} tokens'.format(
                oracle.vacancy_fee / 10 ** decimals,
                user_balance)
        else:
            form = VacancyForm(request.POST)
            if form.is_valid():
                txn_hash = oracle.new_vacancy(args['obj'].contract_address,
                                              int(form.cleaned_data['allowed_amount']) * 10 ** decimals,
                                              int(form.cleaned_data['interview_fee']) * 10 ** decimals)
                if txn_hash:
                    new_vac = form.save(commit=False)
                    new_vac.employer = args['obj']
                    new_vac.save()
                    form.save_m2m()
                    save_txn_to_history.delay(request.user.id, txn_hash,
                                              'Creation of a new vacancy: {}'.format(form.cleaned_data['title']))
                    save_txn.delay(txn_hash, 'NewVacancy', request.user.id, new_vac.id)
                    return redirect(vacancy, vacancy_id=new_vac.id)
                else:
                    args['error'] = 'Error while creation new vacancy'
    args['form'] = form
    if args['role'] == 'candidate':
        args['error'] = 'Candidate cannot place a vacancy'
    return render(request, 'vacancy/new_vacancy.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def vacancy_edit(request, vacancy_id):
    args = {}
    args['vac_o'] = get_object_or_404(Vacancy, employer__user=request.user, pk=vacancy_id)
    if request.method == 'POST':
        form = EditVacancyForm(request.POST, instance=args['vac_o'])
        if form.is_valid():
            form.save()
            return redirect(vacancy, vacancy_id=vacancy_id)
    else:
        form = EditVacancyForm(instance=args['vac_o'])
    args['form'] = form
    return render(request, 'vacancy/vacancy_edit.html', args)


def vacancy(request, vacancy_id):
    args = {}
    try:
        args['vacancy'] = Vacancy.objects.get(id=vacancy_id)
        args['role'], args['obj'] = request.role, request.role_object
        args['net_url'] = django_settings.NET_URL
        if args['role'] == 'candidate':
            args['cvs'] = CurriculumVitae.objects.filter(candidate=args['obj'], published=True)
        return render(request, 'vacancy/vacancy_full.html', args)
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

    save_txn.delay(txn_hash, 'Subscribe', request.user.id, vac_o.id)

    save_txn_to_history.delay(request.user.id, txn_hash, 'Subscribe to vacancy {}'.format(vac_o.title))
    return redirect(vacancy, vacancy_id=vacancy_id)


def vacancy_tests(request, vacancy_id):
    args = {'vacancy': get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user),
            'tests': VacancyTest.objects.filter(vacancy_id=vacancy_id)}
    return render(request, 'vacancy/vacancy_tests.html', args)


def vacancy_test_new(request, vacancy_id):
    args = {'vacancy': get_object_or_404(Vacancy, id=vacancy_id, employer__user=request.user)}
    return render(request, 'vacancy/new_test.html', args)


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

        save_txn.delay(txn_hash, 'vacancyChange', request.user.id, vacancy_id)
        save_txn_to_history.delay(request.user.id, txn_hash, 'Change vacancy {} status'.format(vac_o.contract_address))
    return redirect('profile')


@login_required
@choose_role_required(redirect_url='/role/')
def vacancy_all(request):
    args = {}
    args['role'], args['obj'] = request.role, request.role_object
    if args['role'] == 'candidate':
        return redirect('profile')
    elif args['role'] == 'employer':
        args['vacancies'] = Vacancy.objects.filter(employer=args['obj']).order_by('-created_at')
        return render(request, 'vacancy/vacancies_all.html', args)
    raise Http404


class OfferVacancyView(RedirectView):

    pattern_name = 'cv'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.role != _EMPLOYER:
            return redirect('cv', cv_id=kwargs['cv_id'])
        vac_o = get_object_or_404(Vacancy, id=kwargs['vacancy_id'], employer=self.request.role_object)
        cv_o = get_object_or_404(CurriculumVitae, id=kwargs['cv_id'])
        VacancyOffer.objects.get_or_create(vacancy=vac_o, cv=cv_o)
        return super().get_redirect_url(cv_id=kwargs['cv_id'])

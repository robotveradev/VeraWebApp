from account.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from web3.utils.validation import validate_address
from cv.models import CurriculumVitae
from jobboard.forms import LearningForm, WorkedForm, CertificateForm, EmployerForm, CandidateForm
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.employer import EmployerHandler
from jobboard.tasks import save_txn_to_history, save_txn
from .handlers.candidate import CandidateHandler
from .models import Employer, Candidate, TransactionHistory
from vacancy.models import Vacancy
from .decorators import choose_role_required, role_required
from .handlers.oracle import OracleHandler
from django.conf import settings as django_settings
from django.db.models import Q
from .filters import VacancyFilter, CVFilter

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'

SORTS = [{'id': 1, 'order': '-salary_from', 'title': 'by salary descending', 'type': 'sort'},
         {'id': 2, 'order': 'salary_from', 'title': 'by salary ascending', 'type': 'sort'},
         {'id': 3, 'order': '-updated_at', 'title': 'by date', 'type': 'sort'}]

CVS_SORTS = [{'id': 1, 'order': '-position__salary_from', 'title': 'by salary descending', 'type': 'sort'},
             {'id': 2, 'order': 'position__salary_from', 'title': 'by salary ascending', 'type': 'sort'},
             {'id': 3, 'order': '-updated_at', 'title': 'by date', 'type': 'sort'}]


def index(request):
    return render(request, 'jobboard/index.html', {})


class FindJobView(TemplateView):
    template_name = 'jobboard/find_job.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancies = Vacancy.objects.filter(enabled=True, employer__enabled=True).exclude(contract_address=None)
        self.vacancies_filter = None
        self.cvs = CurriculumVitae.objects
        self.context = {}

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.get_context_data(**kwargs)
        self.set_vacancies_filter()
        self.sort_vacancies_filter()
        paginator = Paginator(self.vacancies_filter, 15)
        self.context.update({'vacancies': paginator.get_page(request.GET.get('page')),
                             'sorts': SORTS})
        return self.render_to_response(self.context)

    def set_vacancies_filter(self):
        if 'filter' not in self.request.GET:
            self.set_filter_for_relevant_vacancies()
        else:
            self.set_filter_by_parameters()

    def set_filter_for_relevant_vacancies(self):
        if self.request.role == _CANDIDATE:
            cvs = self.cvs.filter(candidate=self.request.role_object, published=True)
            specs_list = list(set([item['specialisations__id'] for item in cvs.values('specialisations__id') if
                                   item['specialisations__id'] is not None]))
            keywords_list = list(
                set([item['keywords__id'] for item in cvs.values('keywords__id') if item['keywords__id'] is not None]))
            vacs = self.vacancies.filter(Q(specialisations__in=specs_list) |
                                         Q(keywords__in=keywords_list)).distinct()
            self.vacancies_filter = vacs
        else:
            self.vacancies_filter = self.vacancies
        self.context.update({'all': self.vacancies})

    def set_filter_by_parameters(self):
        self.vacancies_filter = VacancyFilter(self.request.GET, self.vacancies).qs
        self.context.update({'all': self.vacancies_filter})

    def sort_vacancies_filter(self):
        if 'sort' in self.request.GET:
            sort_by = get_item(SORTS, int(self.request.GET.get('sort')))
            if not sort_by:
                sort_by = SORTS[2]
        else:
            sort_by = SORTS[2]
        self.context.update({'selected_sort': sort_by})
        self.vacancies_filter = self.vacancies_filter.order_by(sort_by['order'])


class FindCVView(TemplateView):
    template_name = 'jobboard/find_cv.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.cvs = CurriculumVitae.objects.filter(published=True, candidate__enabled=True)
        self.cvs_filter = None
        self.vacs = Vacancy.objects.filter(enabled=True)
        self.context = {}

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.get_context_data(**kwargs)
        self.set_cvs_filter()
        self.sort_cvs_filter()
        paginator = Paginator(self.cvs_filter, 15)
        self.context.update({'cvs': paginator.get_page(request.GET.get('page')),
                             'sorts': CVS_SORTS})
        return self.render_to_response(self.context)

    def set_cvs_filter(self):
        if 'filter' not in self.request.GET:
            self.set_filter_for_relevant_cvs()
        else:
            self.set_filter_by_parameters()

    def set_filter_for_relevant_cvs(self):
        if self.request.role == _EMPLOYER:
            vacs = self.vacs.filter(employer=self.request.role_object, enabled=True)
            specs_list = list(set([item['specialisations__id'] for item in vacs.values('specialisations__id') if
                                   item['specialisations__id'] is not None]))
            keywords_list = list(
                set([item['keywords__id'] for item in vacs.values('keywords__id') if item['keywords__id'] is not None]))
            cvs = self.cvs.filter(Q(specialisations__in=specs_list) |
                                  Q(keywords__in=keywords_list)).exclude(
                candidate__contract_address=None).distinct()
            self.cvs_filter = cvs
        else:
            self.cvs_filter = self.cvs
        self.context.update({'all': self.cvs})

    def set_filter_by_parameters(self):
        self.cvs_filter = CVFilter(self.request.GET, self.cvs).qs
        self.context.update({'all': self.cvs_filter})

    def sort_cvs_filter(self):
        if 'sort' in self.request.GET:
            sort_by = get_item(CVS_SORTS, int(self.request.GET.get('sort')))
            if not sort_by:
                sort_by = CVS_SORTS[2]
        else:
            sort_by = CVS_SORTS[2]
        self.context.update({'selected_sort': sort_by})
        self.cvs_filter = self.cvs_filter.order_by(sort_by['order'])


class ChooseRoleView(TemplateView):
    template_name = 'jobboard/choose_role.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        role = request.POST.get('role')
        if role == _EMPLOYER:
            _form = EmployerForm(request.POST)
        elif role == 'candidate':
            _form = CandidateForm(request.POST)
        else:
            return redirect('choose_role')
        if _form.is_valid():
            role_o = _form.save(commit=False)
            role_o.user = request.user
            role_o.save()
            if hasattr(request.GET, 'next'):
                return HttpResponseRedirect(request.GET['next'])
            return redirect('profile')
        else:
            context = self.get_context_data(**kwargs)
            context['errors'] = _form.errors
            return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        if request.role is not None:
            return redirect('profile')
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class ProfileView(TemplateView):
    template_name = 'jobboard/profile.html'

    @method_decorator(login_required)
    @method_decorator(choose_role_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if request.role is not None:
            context.update(self.get_current_object_data(request))
        return self.render_to_response(context)

    @staticmethod
    def get_current_object_data(request):
        data = {}
        if request.role == _EMPLOYER:
            vacancies = Vacancy.objects.filter(employer=request.role_object)
            data['vacancies'] = vacancies.order_by('-created_at')[:3]
            data['vacancies_count'] = vacancies.count()
        elif request.role == 'candidate':
            data['learning_form'] = LearningForm()
            data['worked_form'] = WorkedForm()
            data['certificate_form'] = CertificateForm()
            data['cvs'] = CurriculumVitae.objects.filter(candidate=request.role_object)
        return data


class GrantRevokeCandidate(View):

    @method_decorator(login_required)
    @method_decorator(choose_role_required)
    @role_required('employer')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action not in ['revoke', 'grant']:
            return redirect('profile')
        else:
            vac_o = get_object_or_404(Vacancy, id=request.POST.get('vacancy'), employer=request.role_object)
            can_o = get_object_or_404(Candidate, id=request.POST.get('candidate'))
            employer_handler = EmployerHandler(django_settings.WEB_ETH_COINBASE,
                                               request.role_object.contract_address)
            oracle = OracleHandler()
            oracle.unlockAccount()
            if action == 'revoke':
                txn_hash = employer_handler.revoke_access_to_candidate(vac_o.contract_address,
                                                                       can_o.contract_address)
            else:
                txn_hash = employer_handler.grant_access_to_candidate(vac_o.contract_address,
                                                                      can_o.contract_address)

            self.save_txn(vac=vac_o, can=can_o, txn_hash=txn_hash, action=action)
            return redirect('vacancy', vacancy_id=vac_o.id)

    @staticmethod
    def save_txn(**kwargs):
        user_id = kwargs['vac'].employer.user.id
        save_txn.delay(kwargs['txn_hash'], 'EmpAnswer', user_id, kwargs['can'].id,
                       kwargs['vac'].id)
        save_txn_to_history.delay(user_id, kwargs['txn_hash'],
                                  'Candidate {} {}{} to vacancy {}'.format(kwargs['can'].contract_address,
                                                                           kwargs['action'],
                                                                           'ed' if kwargs['action'] == 'grant' else 'd',
                                                                           kwargs['vac'].contract_address))
        save_txn_to_history.delay(kwargs['can'].user_id, kwargs['txn_hash'],
                                  'Employer {} {} your candidacy to vacancy {}'.format(
                                      kwargs['vac'].employer.contract_address,
                                      kwargs['action'],
                                      kwargs['vac'].contract_address))


def employer_about(request, employer_id):
    args = {}
    args['employer'] = get_object_or_404(Employer, id=employer_id)
    if args['employer'].user == request.user:
        return redirect('profile')
    args['vacancies'] = Vacancy.objects.filter(employer_id=employer_id, enabled=True)
    return render(request, 'jobboard/employer_about.html', args)


def change_contract_status(request):
    if request.role:
        oracle = OracleHandler()

        if request.role_object.enabled:
            txn_hash = oracle.pause_contract(request.role_object.contract_address)
        elif request.role_object.enabled is False:
            txn_hash = oracle.unpause_contract(request.role_object.contract_address)
        else:
            txn_hash = False

        if txn_hash:
            request.role_object.enabled = None
            request.role_object.save()
            save_txn.delay(txn_hash, request.role + 'Change', request.user.id, request.role_object.id)
            save_txn_to_history.delay(request.role_object.user_id, txn_hash,
                                      '{} change contract {} status'.format(request.role.capitalize(),
                                                                            request.role_object.contract_address))
    return redirect('profile')


def transactions(request):
    args = {'net_url': django_settings.NET_URL}
    all_txns = TransactionHistory.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(all_txns, request.GET.get('list') or 25)
    page = request.GET.get('page')
    args['txns'] = paginator.get_page(page)
    return render(request, 'jobboard/transactions.html', args)


def get_item(periods, f_id):
    for item in periods:
        if item['id'] == f_id:
            return item
    return False


def get_relevant(request, limit=None):
    if request.role == _EMPLOYER:
        return Vacancy.objects.filter(employer=request.role_object)
    elif request.role == _CANDIDATE:
        cvs = CurriculumVitae.objects.filter(candidate=request.role_object, published=True)
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
@choose_role_required
def withdraw(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        amount = request.POST.get('amount')
        if request.role_object.contract_address is None:
            return redirect('profile')
        try:
            validate_address(address)
        except ValueError:
            return HttpResponse('Invalid address')
        else:
            oracle = OracleHandler()
            coin_h = CoinHandler(django_settings.VERA_COIN_CONTRACT_ADDRESS)
            user_balance = coin_h.balanceOf(request.role_object.contract_address)
            if int(float(amount) * 10 ** 18) > user_balance:
                return HttpResponse('You do not have so many coins', status=200)
            else:
                txn_hash = oracle.withdraw(request.role_object.contract_address, address, int(float(amount) * 10 ** 18))
                save_txn_to_history.delay(request.role_object.user_id, txn_hash,
                                          'Withdraw {} Vera token from {} to {}'.format(amount,
                                                                                        request.role_object.contract_address,
                                                                                        address))
                save_txn.delay(txn_hash, 'Withdraw', request.user.id, request.role_object.id)
    return redirect('profile')


@login_required
@choose_role_required
def check_agent(request):
    if request.is_ajax():
        if request.method == 'POST':
            agent_address = request.POST.get('agent_address')
            try:
                validate_address(agent_address)
            except ValueError:
                return HttpResponse('Invalid address', status=400)
            else:
                emp_h = EmployerHandler(django_settings.WEB_ETH_COINBASE, request.role_object.contract_address)
                if agent_address.casefold() == django_settings.WEB_ETH_COINBASE.casefold():
                    return HttpResponse('oracle', status=200)
                return HttpResponse(emp_h.is_agent(agent_address), status=200)
        else:
            return HttpResponse('You must use Post request', status=400)


class GrantRevokeAgentView(View):

    @method_decorator(login_required)
    @method_decorator(choose_role_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        action = kwargs['action']
        if action not in ['revoke', 'grant']:
            pass
        else:
            address = request.GET.get('address')
            if address == django_settings.WEB_ETH_COINBASE:
                pass
            else:
                try:
                    validate_address(address)
                except ValueError:
                    pass
                else:
                    oracle = OracleHandler()
                    if action == 'revoke':
                        txn_hash = oracle.revoke_agent(request.role_object.contract_address, address)
                    else:
                        txn_hash = oracle.grant_agent(request.role_object.contract_address, address)
                    save_txn_to_history.delay(request.user.id, txn_hash,
                                              'Revoke access for agent {}'.format(address))
        return redirect('profile')


class NewFactView(View):

    @method_decorator(login_required)
    @method_decorator(choose_role_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.role != _CANDIDATE or request.role_object is None:
            return redirect('profile')
        f_type = request.POST.get('f_type')
        if f_type not in ['learning', 'worked', 'certification']:
            return redirect('profile')
        else:
            if f_type == 'learning':
                form = LearningForm(request.POST)
            elif f_type == 'worked':
                form = WorkedForm(request.POST)
            else:
                form = CertificateForm(request.POST)
            if form.is_valid():
                fact = form.cleaned_data
                fact.update({'type': f_type, 'from': request.role_object.contract_address})
                can_h = CandidateHandler(django_settings.WEB_ETH_COINBASE, request.role_object.contract_address)
                oracle = OracleHandler()
                oracle.unlockAccount()
                txn_hash = can_h.new_fact(fact)
                save_txn_to_history.delay(request.role_object.user_id, txn_hash, 'New "{}" fact added'.format(f_type))
        return redirect('profile')

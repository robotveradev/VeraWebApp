from account.decorators import login_required
from account.views import SignupView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, DetailView, RedirectView, ListView
from web3.utils.validation import validate_address
from cv.models import CurriculumVitae
from jobboard.forms import LearningForm, WorkedForm, CertificateForm, EmployerForm, CandidateForm
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.new_employer import EmployerHandler
from jobboard.mixins import ChooseRoleMixin, OnlyEmployerMixin, OnlyCandidateMixin
from jobboard.tasks import save_txn_to_history, save_txn
from .models import Employer, TransactionHistory, InviteCode
from vacancy.models import Vacancy
from .decorators import choose_role_required
from .handlers.new_oracle import OracleHandler
from django.conf import settings as django_settings
from django.db.models import Q
from .filters import VacancyFilter, CVFilter
from django.contrib import messages

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'

SORTS = [{'id': 1, 'order': '-salary_from', 'title': 'by salary descending', 'type': 'sort'},
         {'id': 2, 'order': 'salary_from', 'title': 'by salary ascending', 'type': 'sort'},
         {'id': 3, 'order': '-updated_at', 'title': 'by date', 'type': 'sort'}]

CVS_SORTS = [{'id': 1, 'order': '-position__salary_from', 'title': 'by salary descending', 'type': 'sort'},
             {'id': 2, 'order': 'position__salary_from', 'title': 'by salary ascending', 'type': 'sort'},
             {'id': 3, 'order': '-updated_at', 'title': 'by date', 'type': 'sort'}]


class FindJobView(TemplateView):
    template_name = 'jobboard/find_job.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancies = Vacancy.objects.filter(published=True, enabled=True, employer__enabled=True)
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
        elif role == _CANDIDATE:
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


class ProfileView(ChooseRoleMixin, TemplateView):
    template_name = 'jobboard/profile.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if request.role is not None:
            context.update(self.get_current_object_data(request))
        return self.render_to_response(context)

    @staticmethod
    def get_current_object_data(request):
        data = {}
        if request.role == _CANDIDATE:
            data['learning_form'] = LearningForm()
            data['worked_form'] = WorkedForm()
            data['certificate_form'] = CertificateForm()
        return data


class EmployerAboutView(DetailView):
    model = Employer
    template_name = 'jobboard/employer_about.html'


class ChangeContractStatus(ChooseRoleMixin, RedirectView):

    def get(self, request, *args, **kwargs):
        request.role_object.enabled = not request.role_object.enabled
        request.role_object.save()
        messages.success(request, 'Contract status has been changed')
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('profile')


class TransactionsView(ChooseRoleMixin, ListView):
    model = TransactionHistory
    paginate_by = 25
    template_name = 'jobboard/transactions.html'
    ordering = '-created_at'

    def get_queryset(self):
        qu = super().get_queryset()
        return qu.filter(user=self.request.user)


def get_item(periods, f_id):
    for item in periods:
        if item['id'] == f_id:
            return item
    return False


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


class GrantRevokeAgentView(ChooseRoleMixin, View):

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


class NewFactView(OnlyCandidateMixin, View):

    def post(self, request, *args, **kwargs):
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
                oracle = OracleHandler()
                oracle.unlockAccount()
                txn_hash = oracle.new_fact(request.role_object.contract_address, fact)
                save_txn_to_history.delay(request.role_object.user_id, txn_hash, 'New "{}" fact added'.format(f_type))
        return redirect('profile')


class ApproveTokenView(OnlyEmployerMixin, RedirectView):
    pattern_name = 'profile'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.already_approved = 0
        self.coin = CoinHandler()
        self.employer_h = EmployerHandler

    def dispatch(self, request, *args, **kwargs):
        self.employer_h = self.employer_h(django_settings.WEB_ETH_COINBASE, request.role_object.contract_address)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.set_already_approved()
        if self.already_approved > 0:
            self.set_already_to_0()
        self.approve_money(request.POST.get('approved_amount'))
        return super().get(request, *args, **kwargs)

    def set_already_approved(self):
        self.already_approved = self.coin.allowance(self.request.role_object.contract_address,
                                                    django_settings.VERA_ORACLE_CONTRACT_ADDRESS)

    def set_already_to_0(self):
        self.employer_h.approve_money(0)

    def approve_money(self, amount):
        tnx_hash = self.employer_h.approve_money(int(amount) * 10 ** 18)
        user_id = self.request.role_object.user.id
        save_txn.delay(tnx_hash, 'tokenApprove', user_id, self.request.role_object.id)
        save_txn_to_history.delay(user_id, tnx_hash, 'Money approved for oracle')


class SignupInviteView(SignupView):

    def generate_username(self, form):
        return form.cleaned_data["email"].strip()

    def get_code(self):
        return self.request.COOKIES.get('invtoken')


class InviteLinkView(RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = None

    def get(self, request, *args, **kwargs):
        try:
            self.code = InviteCode.objects.get(code=kwargs.get('code'), expired=False)
        except InviteCode.DoesNotExist:
            return HttpResponse('Invalid code')
        else:
            self.code.expire()
            hrr = HttpResponseRedirect(reverse('account_signup'))
            hrr.set_cookie('invtoken', self.code.signup_code.code)
            return hrr

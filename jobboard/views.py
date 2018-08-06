from account.compat import is_authenticated
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, RedirectView, ListView
from web3.utils.validation import validate_address

from jobboard.forms import LearningForm, WorkedForm, CertificateForm, AchievementForm
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.employer import EmployerHandler
from jobboard.tasks import save_txn_to_history, save_txn
from member_profile.forms import LanguageItemForm, CitizenshipForm, WorkPermitForm
from member_profile.models import Profile
from users.models import Member
from vacancy.models import Vacancy
from .decorators import choose_role_required
from .filters import VacancyFilter, CPFilter
from .handlers.oracle import OracleHandler
from .models import TransactionHistory

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'

SORTS = [{'id': 1, 'order': '-salary_from', 'title': 'by salary descending', 'type': 'sort'},
         {'id': 2, 'order': 'salary_from', 'title': 'by salary ascending', 'type': 'sort'},
         {'id': 3, 'order': '-updated_at', 'title': 'by date', 'type': 'sort'}]

CPS_SORTS = [{'id': 1, 'order': '-position__salary_from', 'title': 'by salary descending', 'type': 'sort'},
             {'id': 2, 'order': 'position__salary_from', 'title': 'by salary ascending', 'type': 'sort'},
             {'id': 3, 'order': '-updated_at', 'title': 'by date', 'type': 'sort'}]


class FindJobView(TemplateView):
    template_name = 'jobboard/find_job.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancies = Vacancy.objects.filter(published=True, enabled=True)
        self.vacancies_filter = None
        self.context = {}

    def get(self, request, *args, **kwargs):
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
        if is_authenticated(self.request.user):
            specs_list = list(set([i.id for i in self.request.user.profile.specialisations.all()]))
            keywords_list = list(set([i.id for i in self.request.user.profile.keywords.all()]))
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


class FindProfilesView(TemplateView):
    template_name = 'jobboard/find_profiles.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.profiles = Profile.objects.all()
        self.profiles_filter = None
        self.vacs = Vacancy.objects.filter(enabled=True)
        self.context = {}

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.get_context_data(**kwargs)
        self.set_profiles_filter()
        self.sort_profiles_filter()
        paginator = Paginator(self.profiles_filter, 15)
        self.context.update({'profiles': paginator.get_page(request.GET.get('page')),
                             'sorts': CPS_SORTS})
        return self.render_to_response(self.context)

    def set_profiles_filter(self):
        if 'filter' not in self.request.GET:
            self.set_filter_for_relevant_profiles()
        else:
            self.set_filter_by_parameters()

    def set_filter_for_relevant_profiles(self):
        if is_authenticated(self.request.user):
            vacs = Vacancy.objects.filter(company__in=self.request.user.companies, enabled=True)
            specs_list = list(set([item['specialisations__id'] for item in vacs.values('specialisations__id') if
                                   item['specialisations__id'] is not None]))
            keywords_list = list(
                set([item['keywords__id'] for item in vacs.values('keywords__id') if item['keywords__id'] is not None]))
            profiles = self.profiles.filter(Q(specialisations__in=specs_list) |
                                            Q(keywords__in=keywords_list)).exclude(
                member__contract_address=None).distinct()
            self.profiles_filter = profiles
        else:
            self.profiles_filter = self.profiles
        self.context.update({'all': self.profiles})

    def set_filter_by_parameters(self):
        self.profiles_filter = CPFilter(self.request.GET, self.profiles).qs
        self.context.update({'all': self.profiles_filter})

    def sort_profiles_filter(self):
        if 'sort' in self.request.GET:
            sort_by = get_item(CPS_SORTS, int(self.request.GET.get('sort')))
            if not sort_by:
                sort_by = CPS_SORTS[2]
        else:
            sort_by = CPS_SORTS[2]
        self.context.update({'selected_sort': sort_by})
        self.profiles_filter = self.profiles_filter.order_by(sort_by['order'])


class ProfileView(TemplateView):
    template_name = 'jobboard/profile.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.get_forms())
        return ctx

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('complete_profile')
        return super().get(request, *args, **kwargs)

    @staticmethod
    def get_forms():
        data = {'learning_form': LearningForm(),
                'worked_form': WorkedForm(),
                'certificate_form': CertificateForm(),
                'language_form': LanguageItemForm(),
                'citizenship_form': CitizenshipForm(),
                'work_permit_form': WorkPermitForm(),
                'achievement_form': AchievementForm()}
        return data


class ChangeContractStatus(RedirectView):

    def get(self, request, *args, **kwargs):
        request.role_object.enabled = not request.role_object.enabled
        request.role_object.save()
        messages.success(request, 'Contract status has been changed')
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('profile')


class TransactionsView(ListView):
    model = TransactionHistory
    paginate_by = 10
    template_name = 'jobboard/transactions.html'
    ordering = '-created_at'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_queryset(self):
        qu = super().get_queryset()
        return qu.filter(user=self.request.user.id)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'count': self.get_queryset().count()})
        return ctx


def get_item(periods, f_id):
    for item in periods:
        if item['id'] == f_id:
            return item
    return False


class WithdrawView(RedirectView):
    pattern_name = 'profile'

    def dispatch(self, request, *args, **kwargs):
        if request.user.contract_address is None:
            return super().get(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        address = request.POST.get('address')
        amount = request.POST.get('amount')
        try:
            validate_address(address)
        except ValueError:
            messages.warning(request, 'Invalid address')
        else:
            coin_h = CoinHandler()
            user_balance = coin_h.balanceOf(request.user.contract_address)
            if int(float(amount) * 10 ** 18) > user_balance:
                return messages.warning(request, 'You do not have so many tokens')

            from jobboard.tasks import withdraw_tokens
            withdraw_tokens.delay(request.user.id, request.user.contract_address, address, amount)
        return super().get(request, *args, **kwargs)


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
                emp_h = EmployerHandler(contract_address=request.role_object.contract_address)
                if agent_address.casefold() == django_settings.WEB_ETH_COINBASE.casefold():
                    return HttpResponse('oracle', status=200)
                return HttpResponse(emp_h.is_agent(agent_address), status=200)
        else:
            return HttpResponse('You must use Post request', status=400)


class GrantRevokeAgentView(View):

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
                    save_txn_to_history.delay(request.user.id, txn_hash.hex(),
                                              'Revoke access for agent {}'.format(address))
        return redirect('profile')


class NewFactView(View):

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
                save_txn_to_history.delay(request.role_object.user_id, txn_hash.hex(),
                                          'New "{}" fact added'.format(f_type))
        return redirect('profile')


class ApproveTokenView(RedirectView):
    pattern_name = 'profile'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.already_approved = 0
        self.coin = CoinHandler()
        self.employer_h = None

    def dispatch(self, request, *args, **kwargs):
        self.employer_h = EmployerHandler(contract_address=request.role_object.contract_address)
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
        self.employer_h.approve_money(amount=0)

    def approve_money(self, amount):
        tnx_hash = self.employer_h.approve_money(amount=int(amount) * 10 ** 18)
        user_id = self.request.role_object.user.id
        save_txn.delay(tnx_hash.hex(), 'tokenApprove', user_id, self.request.role_object.id)
        save_txn_to_history.delay(user_id, tnx_hash.hex(), 'Money approved for oracle')


class GetFreeCoinsView(RedirectView):
    pattern_name = 'profile'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        coin_h = CoinHandler()
        OracleHandler().unlockAccount()
        txn_hash = coin_h.transfer(request.user.contract_address, 10000 * 10 ** 18)
        OracleHandler().lockAccount()
        save_txn_to_history.delay(request.user.id, txn_hash.hex(), 'Free coins added.')
        return super().get(request, *args, **kwargs)


class CandidateProfileView(DetailView):
    model = Member
    template_name = 'jobboard/member_profile.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = None

    def get_object(self, queryset=None):
        can = get_object_or_404(Member, username=self.kwargs.get('username'))
        return can


class FindFieldView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not is_authenticated(request.user):
            return HttpResponse(status=403)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        model = kwargs.get('model')
        field = kwargs.get('field')
        name = request.POST.get('name')
        from django.contrib.contenttypes.models import ContentType
        try:
            model_object = ContentType.objects.get(model=model)
        except ContentType.DoesNotExist:
            return JsonResponse({})
        else:
            model_class = model_object.model_class()
            if not hasattr(model_class, field):
                return JsonResponse({}, status=200)
            filters = {'{}__icontains'.format(field): name}
            finded = model_class.objects.values('id', field).filter(**filters)[:10]
            dict_f = [{'id': i['id'], field: i['name']} for i in finded]
            return JsonResponse(dict_f, safe=False, status=200)

from account.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, CreateView, UpdateView, DetailView, ListView
from cv.models import CurriculumVitae
from jobboard.decorators import choose_role_required, role_required
from jobboard.handlers.candidate import CandidateHandler
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.oracle import OracleHandler
from django.conf import settings
from jobboard.mixins import OnlyEmployerMixin
from statistic.decorators import statistical
from vacancy.forms import VacancyForm, EditVacancyForm
from vacancy.models import Vacancy, CVOnVacancy, VacancyOffer
from jobboard.tasks import save_txn_to_history, save_txn
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'

MESSAGES = {'not_enough_tokens': _('The cost of placing a vacancy of {} tokens. Your balance {} tokens.'),
            'new_vacancy': _('New vacancy "{}" successfully added'), }


class CreateVacancyView(OnlyEmployerMixin, CreateView):
    template_name = 'vacancy/new_vacancy.html'
    model = Vacancy
    form_class = VacancyForm
    success_url = reverse_lazy('vacancy_all')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        return self.check_balance(form)

    def check_balance(self, form):
        coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
        oracle = OracleHandler()
        decimals = coin_h.decimals
        user_balance = coin_h.balanceOf(self.request.role_object.contract_address)
        if user_balance < oracle.vacancy_fee:
            messages.warning(self.request, MESSAGES['not_enough_tokens'].format(
                oracle.vacancy_fee / 10 ** decimals,
                user_balance / 10 ** decimals))
            return super().form_invalid(form)
        form.instance.employer = self.request.role_object
        form.instance.allowed_amount = form.cleaned_data['allowed_amount']
        form.instance.interview_fee = form.cleaned_data['interview_fee']
        messages.success(self.request, MESSAGES['new_vacancy'].format(form.cleaned_data['title']))
        return super().form_valid(form)


class VacancyEditView(OnlyEmployerMixin, UpdateView):
    model = Vacancy
    form_class = EditVacancyForm
    template_name = 'vacancy/vacancy_edit.html'

    def get_object(self, queryset=None):
        queryset = super().get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk, employer=self.request.role_object)
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404
        return obj

    def get_success_url(self):
        return reverse('vacancy', kwargs={'pk': self.object.id})


class VacancyView(DetailView):
    template_name = 'vacancy/vacancy_full.html'
    model = Vacancy

    @method_decorator(statistical)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@role_required('candidate')
def subscribe_to_vacancy(request, vacancy_id, cv_id):
    can_o = request.role_object
    vac_o = get_object_or_404(Vacancy, id=vacancy_id)
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate=can_o)

    if not can_o.contract_address or not vac_o.contract_address:
        raise Http404

    oracle = OracleHandler(settings.WEB_ETH_COINBASE, settings.VERA_ORACLE_CONTRACT_ADDRESS)
    oracle.unlockAccount()
    can_h = CandidateHandler(settings.WEB_ETH_COINBASE, can_o.contract_address)
    txn_hash = can_h.subscribe_to_interview(vac_o.contract_address)

    cvonvac = CVOnVacancy()
    cvonvac.cv = cv_o
    cvonvac.vacancy = vac_o
    cvonvac.save()

    save_txn.delay(txn_hash, 'Subscribe', request.user.id, vac_o.id)

    save_txn_to_history.delay(request.user.id, txn_hash, 'Subscribe to vacancy {}'.format(vac_o.title))
    return redirect('vacancy', pk=vacancy_id)


class ChangeVacancyStatus(OnlyEmployerMixin, RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.object.id})

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Vacancy, pk=kwargs.get('pk', None), employer=request.role_object)
        if self.object.enabled is None:
            pass
        else:
            self.object.enabled = None
            self.object.save()
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))


class VacanciesListView(OnlyEmployerMixin, ListView):
    model = Vacancy
    template_name = 'vacancy/vacancies_all.html'
    paginate_by = 15
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(employer=self.request.role_object)
        return queryset


class OfferVacancyView(OnlyEmployerMixin, RedirectView):
    pattern_name = 'cv'

    def get_redirect_url(self, *args, **kwargs):
        vac_o = get_object_or_404(Vacancy, id=kwargs['vacancy_id'], employer=self.request.role_object)
        cv_o = get_object_or_404(CurriculumVitae, id=kwargs['cv_id'])
        VacancyOffer.objects.get_or_create(vacancy=vac_o, cv=cv_o)
        return super().get_redirect_url(pk=kwargs['cv_id'])

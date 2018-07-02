import os

from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView, CreateView, UpdateView, DetailView, ListView
from web3 import Web3

from candidateprofile.models import CandidateProfile
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.oracle import OracleHandler
from jobboard.mixins import OnlyEmployerMixin, OnlyCandidateMixin
from jobboard.models import Candidate
from statistic.decorators import statistical
from vacancy.forms import VacancyForm, EditVacancyForm
from vacancy.models import Vacancy, CandidateOnVacancy, VacancyOffer

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'

MESSAGES = {'allow': _('You must approve the tokens for the oracle.'),
            'empty_exam': _('One or more actions do not have an exam.'),
            'empty_interview': _('One or more actions do not have an interview.'),
            'disabled_profile': _('Your profile has no position. You must set position it for subscribe.'),
            'disabled_vacancy': _('Vacancy {} now disabled. You cannot subscribe to disabled vacancy.'),
            'pipeline_doesnot_exist': 'You must add pipeline to enable vacancy',
            'need_more_actions': 'You must add more actions for pipeline', }


class CreateVacancyView(OnlyEmployerMixin, CreateView):
    template_name = 'vacancy/new_vacancy.html'
    form_class = VacancyForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
        self.request = None

    def get(self, request, *args, **kwargs):
        if not request.role_object.companies.exists():
            return redirect('new_company')
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'employer': self.request.role_object})
        return kwargs

    def get_success_url(self):
        return reverse('vacancy', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        return self.process_form_instance(form)

    def process_form_instance(self, form):
        form.instance.allowed_amount = form.cleaned_data['allowed_amount']
        form.instance.uuid = Web3.toHex(os.urandom(32))
        return super().form_valid(form)


class VacancyEditView(OnlyEmployerMixin, UpdateView):
    model = Vacancy
    form_class = EditVacancyForm
    template_name = 'vacancy/vacancy_edit.html'

    def get_object(self, queryset=None):
        queryset = super().get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk, company__employer=self.request.role_object)
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


class SubscribeToVacancyView(OnlyCandidateMixin, RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vacancy = None
        self.request = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': kwargs.get('vacancy_id')})

    def get(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, id=kwargs.get('vacancy_id'))
        return self.check_vac_profile(*args, **kwargs)

    def check_vac_profile(self, *args, **kwargs):
        if not self.vacancy.enabled:
            messages.error(self.request, MESSAGES['disabled_vacancy'].format(self.vacancy.title))
        elif not self.request.role_object.enabled:
            messages.error(self.request, MESSAGES['disabled_profile'].format(self.request.role_object.profile.title))
        if not self.vacancy.enabled or not self.request.role_object.enabled:
            return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))
        else:
            return self.subscribe(*args, **kwargs)

    def subscribe(self, *args, **kwargs):
        CandidateOnVacancy.objects.create(candidate=self.request.role_object, vacancy=self.vacancy)
        return super().get(self.request, *args, **kwargs)


class ChangeVacancyStatus(OnlyEmployerMixin, RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
        self.errors = []

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.object.id})

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Vacancy, pk=kwargs.get('pk', None), company__employer=request.role_object)
        if not hasattr(self.object, 'pipeline'):
            self.errors.append('pipeline_doesnot_exist')
        else:
            self.check_employer()
            self.check_actions()
        if not self.errors:
            if self.object.enabled is not None:
                self.object.enabled = None
                self.object.change_status = True
                self.object.save()
        else:
            for error in set(self.errors):
                messages.warning(request, MESSAGES[error])
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def check_employer(self):
        oracle = OracleHandler()
        coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
        vac_allowance = oracle.vacancy(self.object.uuid)['allowed_amount']
        oracle_allowance = coin_h.allowance(self.object.company.employer.contract_address, oracle.contract_address)
        if oracle_allowance < vac_allowance:
            self.errors.append('allow')

    def check_actions(self):
        if hasattr(self.object, 'pipeline'):
            if not self.object.pipeline.actions.exists():
                self.errors.append('need_more_actions')
            for action in self.object.pipeline.actions.all():
                if action.action_type.condition_of_passage:
                    method = getattr(self, 'check_' + action.action_type.condition_of_passage)
                    method(action)

    def check_exam(self, action):
        if not hasattr(action, 'exam'):
            self.errors.append('empty_exam')

    def check_interview(self, action):
        if not hasattr(action, 'interview'):
            self.errors.append('empty_interview')


class VacanciesListView(OnlyEmployerMixin, ListView):
    model = Vacancy
    template_name = 'vacancy/vacancies_all.html'
    paginate_by = 15
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(company__employer=self.request.role_object)
        return queryset


class OfferVacancyView(OnlyEmployerMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        vac_o = get_object_or_404(Vacancy, id=kwargs['vacancy_id'], company__employer=self.request.role_object)
        cp_o = get_object_or_404(CandidateProfile, id=kwargs['profile_id'])
        VacancyOffer.objects.get_or_create(vacancy=vac_o, profile=cp_o)
        return reverse('candidate_profile', kwargs={'username': cp_o.candidate.user.username})


class UpdateAllowedView(OnlyEmployerMixin, UpdateView):
    model = Vacancy
    fields = ('allowed_amount',)

    def post(self, request, *args, **kwargs):
        vacancy = get_object_or_404(Vacancy, pk=kwargs.get('pk'))
        if vacancy.owner != request.user:
            return HttpResponse(status=403)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.allowed_changed = True
        form.save()
        return HttpResponse('ok', status=200)

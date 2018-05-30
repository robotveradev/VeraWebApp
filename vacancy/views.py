import os

from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView, CreateView, UpdateView, DetailView, ListView
from web3 import Web3

from candidateprofile.models import CandidateProfile
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.new_oracle import OracleHandler
from jobboard.mixins import OnlyEmployerMixin, OnlyCandidateMixin
from statistic.decorators import statistical
from vacancy.forms import VacancyForm, EditVacancyForm
from vacancy.models import Vacancy, CVOnVacancy, VacancyOffer

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'

MESSAGES = {'allow': _('You must approve the tokens for the oracle.'),
            'empty_exam': _('One or more actions do not have an exam.'),
            'empty_interview': _('One or more actions do not have an interview.'),
            'disabled_cv': _('Your profile has no position. You must set position it for subscribe.'),
            'disabled_vacancy': _('Vacancy {} now disabled. You cannot subscribe to disabled vacancy.')}


class CreateVacancyView(OnlyEmployerMixin, CreateView):
    template_name = 'vacancy/new_vacancy.html'
    form_class = VacancyForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
        self.request = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'employer': self.request.role_object})
        return kwargs

    def get_success_url(self):
        return reverse('pipeline_constructor', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        return self.process_form_instance(form)

    def process_form_instance(self, form):
        form.instance.allowed_amount = form.cleaned_data['allowed_amount']
        form.instance.uuid = Web3.toHex(os.urandom(15))
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
        self.cv = None
        self.vacancy = None
        self.request = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': kwargs.get('vacancy_id')})

    def get(self, request, *args, **kwargs):
        self.cv = get_object_or_404(CandidateProfile, id=kwargs.get('cv_id'), candidate=request.role_object)
        self.vacancy = get_object_or_404(Vacancy, id=kwargs.get('vacancy_id'))
        return self.check_vac_cv(*args, **kwargs)

    def check_vac_cv(self, *args, **kwargs):
        if not self.vacancy.enabled:
            messages.error(self.request, MESSAGES['disabled_vacancy'].format(self.vacancy.title))
        elif not self.cv.enabled:
            messages.error(self.request, MESSAGES['disabled_cv'].format(self.cv.title))
        if not self.vacancy.enabled or not self.cv.enabled:
            return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))
        else:
            return self.subscribe(*args, **kwargs)

    def subscribe(self, *args, **kwargs):
        CVOnVacancy.objects.create(cv=self.cv, vacancy=self.vacancy)
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
        self.check_employer()
        self.check_actions()
        if not self.errors:
            if self.object.enabled is not None:
                self.object.enabled = None
                self.object.save()
        else:
            for error in set(self.errors):
                messages.warning(request, MESSAGES[error])
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def check_employer(self):
        oracle = OracleHandler()
        coin_h = CoinHandler(settings.VERA_COIN_CONTRACT_ADDRESS)
        vac_allowance = oracle.get_vacancy(self.object.uuid)[2]
        oracle_allowance = coin_h.allowance(self.object.company.employer.contract_address, oracle.contract_address)
        if oracle_allowance < vac_allowance:
            self.errors.append('allow')

    def check_actions(self):
        for action in self.object.pipeline.actions.all():
            if action.type.condition_of_passage:
                method = getattr(self, 'check_' + action.type.condition_of_passage)
                method(action)

    def check_quiz(self, action):
        if not action.exam.exists():
            self.errors.append('empty_exam')
        else:
            print('VOT: {}'.format(action.exam.all()))

    def check_interview(self, action):
        if not action.interview.exists():
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
        cp_o = get_object_or_404(CandidateProfile, id=kwargs['cv_id'])
        VacancyOffer.objects.get_or_create(vacancy=vac_o, cv=cp_o)
        return reverse('candidate_profile', kwargs={'username': cp_o.candidate.user.username})


class UpdateAllowedView(OnlyEmployerMixin, UpdateView):
    model = Vacancy
    fields = ('allowed_amount',)

    def post(self, request, *args, **kwargs):
        get_object_or_404(Vacancy, pk=kwargs.get('pk'), employer=request.role_object)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponse('ok', status=200)

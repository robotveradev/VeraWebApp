import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView, CreateView, UpdateView, DetailView
from web3 import Web3

from company.models import Company
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.oracle import OracleHandler
from member_profile.models import Profile
from statistic.decorators import statistical
from users.utils import company_member_role
from vacancy.forms import VacancyForm, EditVacancyForm
from vacancy.models import Vacancy, MemberOnVacancy, VacancyOffer

_EMPLOYER, _CANDIDATE = 'employer', 'candidate'

MESSAGES = {'empty_exam': _('One or more actions do not have an exam.'),
            'empty_interview': _('One or more actions do not have an interview.'),
            'disabled_profile': _('Your profile has no position. You must set position it for subscribe.'),
            'disabled_vacancy': _('Vacancy {} now disabled. You cannot subscribe to disabled vacancy.'),
            'pipeline_doesnot_exist': _('You must add pipeline to enable vacancy.'),
            'need_more_actions': _('You must add more actions for pipeline.'),
            'allow': _('The company does not have enough tokens.'),
            'company_member': _('Company member not allowed to subscribe.')}


class CreateVacancyView(CreateView):
    template_name = 'vacancy/new_vacancy.html'
    form_class = VacancyForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
        self.request = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.companies.exists():
            messages.info(request, 'You must add company first')
            return redirect('new_company')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            company = request.user.companies.get(pk=request.POST.get('company'))
        except Company.DoesNotExist:
            messages.warning(request, 'Invalid company')
        else:
            if request.user not in company.owners:
                messages.warning(request, 'You cannot create vacancy at this company')
                return super().get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'member': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('vacancy', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        return self.process_form_instance(form)

    def process_form_instance(self, form):
        form.instance.created_by = self.request.user
        form.instance.allowed_amount = form.cleaned_data['allowed_amount']
        form.instance.uuid = Web3.toHex(os.urandom(32))
        return super().form_valid(form)


class VacancyEditView(UpdateView):
    model = Vacancy
    form_class = EditVacancyForm
    template_name = 'vacancy/vacancy_edit.html'

    def get_object(self, queryset=None):
        queryset = super().get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
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


class SubscribeToVacancyView(RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vacancy = None
        self.request = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': kwargs.get('vacancy_id')})

    def get(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, id=kwargs.get('vacancy_id'))
        return self.check_vac(*args, **kwargs)

    def check_vac(self, *args, **kwargs):
        if not self.vacancy.enabled:
            messages.error(self.request, MESSAGES['disabled_vacancy'].format(self.vacancy.title))
            return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

        return self.check_profile(*args, **kwargs)

    def check_profile(self, *args, **kwargs):
        role = company_member_role(self.vacancy.company.contract_address, self.request.user.contract_address)
        if role:
            messages.error(self.request, MESSAGES['company_member'])
            return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))
        return self.subscribe(*args, **kwargs)

    def subscribe(self, *args, **kwargs):
        MemberOnVacancy.objects.create(member=self.request.user, vacancy=self.vacancy)
        return super().get(self.request, *args, **kwargs)


class ChangeVacancyStatus(RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.object = None
        self.errors = []

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.object.id})

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Vacancy, pk=kwargs.get('pk', None), company_id__in=request.user.companies)
        if not hasattr(self.object, 'pipeline'):
            self.errors.append('pipeline_doesnot_exist')
        else:
            self.check_company()
            self.check_actions()
        if not self.errors:
            pass
            if self.object.enabled is not None:
                self.object.enabled = None
                self.object.change_status = True
                self.object.change_by = request.user
                self.object.save()
        else:
            for error in set(self.errors):
                messages.warning(request, MESSAGES[error])
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def check_company(self):
        oracle = OracleHandler()
        coin_h = CoinHandler()

        company_balance = coin_h.balanceOf(self.object.company.contract_address)
        allowed_for_vacancies = 0
        for vacancy in self.object.company.vacancies.all():
            allowed_for_vacancies += vacancy.chain_allowed_amount
        if allowed_for_vacancies > company_balance:
            self.errors.append('allow')
        # vac_allowance = oracle.vacancy(self.object.company.contract_address, self.object.uuid)['allowed_amount']
        # oracle_allowance = coin_h.allowance(self.object.company.contract_address, oracle.contract_address)
        # mi = MemberInterface(self.request.user.contract_address)
        # mi.approve_company_tokens()

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


class OfferVacancyView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        vac_o = get_object_or_404(Vacancy, id=kwargs['vacancy_id'], company__employer=self.request.role_object)
        cp_o = get_object_or_404(Profile, id=kwargs['profile_id'])
        VacancyOffer.objects.get_or_create(vacancy=vac_o, profile=cp_o)
        return reverse('member_profile', kwargs={'username': cp_o.member.username})


class UpdateAllowedView(UpdateView):
    model = Vacancy
    fields = ('allowed_amount',)

    def post(self, request, *args, **kwargs):
        vacancy = get_object_or_404(Vacancy, pk=kwargs.get('pk'))
        if request.user not in vacancy.company.owners:
            return HttpResponse(status=403)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.allowed_changed = True
        form.save()
        return HttpResponse('ok', status=200)

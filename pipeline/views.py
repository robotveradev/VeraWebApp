from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView, DetailView, CreateView

from candidateprofile.models import CandidateProfile
from jobboard.handlers.new_employer import EmployerHandler
from jobboard.handlers.oracle import OracleHandler
from jobboard.mixins import OnlyEmployerMixin
from jobboard.tasks import save_txn, save_txn_to_history
from pipeline.models import Action, Pipeline
from vacancy.models import Vacancy


class ApproveActionEmployerView(OnlyEmployerMixin, RedirectView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancy = None
        self.profile = None
        self.employer_h = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.vacancy.id})

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=kwargs.get('vacancy_id'), company__employer=request.role_object)
        self.profile = get_object_or_404(CandidateProfile, pk=kwargs.get('profile_id'))
        self.employer_h = EmployerHandler(settings.WEB_ETH_COINBASE, self.vacancy.employer.contract_address)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.approve_candidate()
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def approve_candidate(self):
        txn_hash = self.employer_h.approve_level_up(self.vacancy.uuid, self.profile.candidate.contract_address)
        save_txn.delay(txn_hash.hex(), 'EmpAnswer', self.request.user.id, self.profile.id, self.vacancy.id)
        save_txn_to_history.delay(self.request.user.id, txn_hash.hex(),
                                  'Candidate {} transferred to the next level.'.format(
                                      self.profile.candidate.contract_address))
        save_txn_to_history.delay(self.profile.candidate.user.id, txn_hash.hex(),
                                  'Candidate {} level up on vacancy {}.'.format(self.profile.candidate.contract_address,
                                                                                self.vacancy.uuid))


class RevokeCandidateView(OnlyEmployerMixin, RedirectView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancy = None
        self.profile = None
        self.employer_h = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.vacancy.id})

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=kwargs.get('vacancy_id'), company__employer=request.role_object)
        self.profile = get_object_or_404(CandidateProfile, pk=kwargs.get('profile_id'))
        self.employer_h = EmployerHandler(settings.WEB_ETH_COINBASE, self.vacancy.employer.contract_address)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.reset_candidate()
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def reset_candidate(self):
        txn_hash = self.employer_h.reset_candidate(self.vacancy.uuid, self.profile.candidate.contract_address)
        save_txn.delay(txn_hash.hex(), 'EmpAnswer', self.request.user.id, self.profile.id, self.vacancy.id)
        save_txn_to_history.delay(self.request.user.id, txn_hash.hex(),
                                  'Candidate {} revoked.'.format(self.profile.candidate.contract_address))
        save_txn_to_history.delay(self.profile.candidate.user.id, txn_hash.hex(),
                                  'Candidate {} revoked on vacancy {}.'.format(self.profile.candidate.contract_address,
                                                                               self.vacancy.uuid))


class ActionDetailView(OnlyEmployerMixin, DetailView):
    model = Action
    context_object_name = 'action'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vacancy = None
        self.action = None
        self.oracle = OracleHandler()

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = Vacancy.objects.get(pk=kwargs.get('pk'))
        self.action = self.oracle.get_action(self.vacancy.uuid, kwargs.get('action_id'))
        self.action['last'] = self.oracle.get_vacancy_pipeline_length(self.vacancy.uuid) - 1 == self.action['id']
        self.set_db_action()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.action

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancy'] = self.vacancy
        return context

    def set_db_action(self):
        try:
            self.action.update(
                {'db_action': Action.objects.get(pipeline__vacancy=self.vacancy, sort=self.action['id'])})
        except Action.DoesNotExist:
            pass


class NewActionView(OnlyEmployerMixin, CreateView):
    model = Action
    fields = ['type', 'pipeline', ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.pipeline = None

    def dispatch(self, request, *args, **kwargs):
        self.pipeline = get_object_or_404(Pipeline, pk=kwargs.get('pk'))
        print(self.request.POST)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        print('here')
        print(self.request.POST)
        form.instance.type = self.request.POST.get('data')
        form.instance.pipeline = self.pipeline
        return super().form_valid(form)

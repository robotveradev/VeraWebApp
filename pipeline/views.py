from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView, DetailView
from cv.models import CurriculumVitae
from jobboard.handlers.new_employer import EmployerHandler
from jobboard.handlers.new_oracle import OracleHandler
from jobboard.mixins import OnlyEmployerMixin
from jobboard.tasks import save_txn, save_txn_to_history
from pipeline.models import Pipeline, ActionType, Action
from vacancy.models import Vacancy
from vacancy.tasks import new_vacancy


class PipelineConstructorView(OnlyEmployerMixin, TemplateView):
    template_name = 'pipeline/constructor.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vacancy = None
        self.pipeline = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_types'] = ActionType.objects.all()
        context['vacancy'] = get_object_or_404(Vacancy, pk=kwargs.get('pk'))
        return context

    def post(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=kwargs.get('pk'), employer=request.role_object)
        self.new_pipeline()
        self.process_actions(request)

        return HttpResponseRedirect(reverse('vacancy', kwargs={'pk': self.vacancy.id}))

    def new_pipeline(self):
        self.pipeline = Pipeline.objects.create(vacancy=self.vacancy)

    def process_actions(self, request):
        action_types = request.POST.getlist('action')
        fees = request.POST.getlist('fee')
        approve = request.POST.getlist('approve')
        actions = []
        for i in range(len(action_types)):
            actions.append(Action(type=ActionType.objects.get(title=action_types[i]), pipeline=self.pipeline, sort=i))
        Action.objects.bulk_create(actions)
        action_types.append('Done')
        fees.append('0')
        approve.append('False')
        contract_actions_dict = {
            'titles': action_types,
            'fees': fees,
            'approve': approve
        }
        new_vacancy.delay(self.vacancy.id, contract_actions_dict)


class ApproveActionEmployerView(OnlyEmployerMixin, RedirectView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancy = None
        self.cv = None
        self.employer_h = EmployerHandler

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.vacancy.id})

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=kwargs.get('vacancy_id'), employer=request.role_object)
        self.cv = get_object_or_404(CurriculumVitae, pk=kwargs.get('cv_id'))
        self.employer_h = self.employer_h(settings.WEB_ETH_COINBASE, self.vacancy.employer.contract_address)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.approve_cv()
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def approve_cv(self):
        txn_hash = self.employer_h.approve_level_up(self.vacancy.uuid, self.cv.uuid)
        save_txn.delay(txn_hash, 'EmpAnswer', self.request.user.id, self.cv.id, self.vacancy.id)
        save_txn_to_history.delay(self.request.user.id, txn_hash,
                                  'Cv {} transferred to the next level.'.format(self.cv.uuid))
        save_txn_to_history.delay(self.cv.candidate.user.id, txn_hash,
                                  'Cv {} level up on vacancy {}.'.format(self.cv.uuid, self.vacancy.uuid))


class RevokeCvEmployerView(OnlyEmployerMixin, RedirectView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancy = None
        self.cv = None
        self.employer_h = EmployerHandler

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.vacancy.id})

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=kwargs.get('vacancy_id'), employer=request.role_object)
        self.cv = get_object_or_404(CurriculumVitae, pk=kwargs.get('cv_id'))
        self.employer_h = self.employer_h(settings.WEB_ETH_COINBASE, self.vacancy.employer.contract_address)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.reset_cv()
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def reset_cv(self):
        txn_hash = self.employer_h.reset_cv(self.vacancy.uuid, self.cv.uuid)
        save_txn.delay(txn_hash, 'EmpAnswer', self.request.user.id, self.cv.id, self.vacancy.id)
        save_txn_to_history.delay(self.request.user.id, txn_hash,
                                  'Cv {} revoked.'.format(self.cv.uuid))
        save_txn_to_history.delay(self.cv.candidate.user.id, txn_hash,
                                  'Cv {} revoked on vacancy {}.'.format(self.cv.uuid, self.vacancy.uuid))


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

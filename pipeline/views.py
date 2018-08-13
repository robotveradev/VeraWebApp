from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView, DetailView, CreateView, UpdateView

from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Transaction
from pipeline.forms import ActionChangeForm
from pipeline.models import Action, Pipeline
from pipeline.tasks import action_with_candidate
from users.models import Member
from users.utils import company_member_role
from vacancy.models import Vacancy


class ApproveActionEmployerView(RedirectView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancy = None
        self.candidate = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.vacancy.id})

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=kwargs.get('vacancy_id'))
        self.candidate = get_object_or_404(Member, pk=kwargs.get('candidate_id'))
        return super().dispatch(request, *args, **kwargs)

    def already_pending(self):
        return Transaction.objects.filter(txn_type='CandidateActionUpDown',
                                          obj_id=self.candidate.id,
                                          vac_id=self.vacancy.id).exists()

    def get(self, request, *args, **kwargs):
        if self.already_pending():
            messages.info(self.request, 'Action with candidate already pending. Please wait.')
        else:
            action_with_candidate.delay(self.vacancy.id, self.candidate.id, 'approve', self.request.user.id)
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))


class ResetCandidateView(RedirectView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancy = None
        self.candidate = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.vacancy.id})

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=kwargs.get('vacancy_id'))
        self.candidate = get_object_or_404(Member, pk=kwargs.get('candidate_id'))
        return super().dispatch(request, *args, **kwargs)

    def already_pending(self):
        return Transaction.objects.filter(txn_type='CandidateActionUpDown',
                                          obj_id=self.candidate.id,
                                          vac_id=self.vacancy.id).exists()

    def get(self, request, *args, **kwargs):
        if self.already_pending():
            messages.info(self.request, 'Action with candidate already pending. Please wait.')
        else:
            action_with_candidate.delay(self.vacancy.id, self.candidate.id, 'reset', request.user.id)
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))


class ActionDetailView(DetailView):
    model = Action
    context_object_name = 'action'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = None

    def get_context_data(self, **kwargs):
        action = self.get_object()
        context = super().get_context_data(**kwargs)

        context['change_form'] = ActionChangeForm(instance=action,
                                                  initial={'fee': action.chain.fee,
                                                           'approvable': action.chain.approvable})
        return context


class NewActionView(CreateView):
    model = Action
    fields = ['action_type', 'pipeline', ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def dispatch(self, request, *args, **kwargs):
        pipeline = get_object_or_404(Pipeline, pk=request.POST.get('pipeline', None))
        user_role = company_member_role(pipeline.vacancy.company.contract_address, request.user.contract_address)
        assert user_role == 'owner', "User can\'t create action for this pipeline"
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('vacancy', kwargs={'pk': self.object.pipeline.vacancy.id})

    def form_valid(self, form):
        form.instance.fee = self.request.POST.get('fee', 0)
        form.instance.approvable = form.instance.action_type.must_approvable or 'approvable' in self.request.POST
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ChangeActionView(UpdateView):
    form_class = ActionChangeForm
    model = Action

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def form_valid(self, form):
        form.instance.fee = self.request.POST.get('fee', 0)
        form.instance.approvable = 'approvable' in self.request.POST
        return super().form_valid(form)


class DeleteActionView(RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.vacancy = None

    def dispatch(self, request, *args, **kwargs):
        action = get_object_or_404(Action, pk=kwargs.get('pk', None))
        self.vacancy = action.pipeline.vacancy
        if action.owner != request.user:
            raise Http404
        action.to_delete = True
        action.save()
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('vacancy', kwargs={'pk': self.vacancy.id})


class CandidateProcessAction(RedirectView):
    """
    Redirect user to page handle action (exam, interview)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = None

    def dispatch(self, request, *args, **kwargs):
        self.action = get_object_or_404(Action, pk=kwargs.get('pk', None))
        vacancy = self.action.pipeline.vacancy
        oracle = OracleHandler()
        mci = oracle.get_member_current_action_index(vacancy.company.contract_address,
                                                     vacancy.uuid,
                                                     request.user.contract_address)
        if mci != self.action.index:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        if self.action.action_type.condition_of_passage is None:
            raise Http404
        if hasattr(self.action, self.action.action_type.condition_of_passage):
            handler = getattr(self.action, self.action.action_type.condition_of_passage)
            return handler.get_candidate_url()

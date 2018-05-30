from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, TemplateView, CreateView
from candidateprofile.models import CandidateProfile
from interview import utils
from interview.forms import ActionInterviewForm
from interview.models import *
from jobboard.mixins import ChooseRoleMixin, OnlyEmployerMixin


class InterviewView(ChooseRoleMixin, TemplateView):
    template_name = 'interview/dialogs.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.action_interview = None
        self.interview = None
        self.cv = None

    def dispatch(self, request, *args, **kwargs):
        self.action_interview = get_object_or_404(ActionInterview, pk=kwargs.get('pk'))
        self.cv = get_object_or_404(CandidateProfile, pk=kwargs.get('cv_id'))
        self.interview, _ = Interview.objects.get_or_create(action_interview=self.action_interview, cv=self.cv)
        return self.check_interview(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['active_dialog'] = self.interview

        if self.request.role_object == self.action_interview.action.pipeline.vacancy.employer:
            context['opponent_uuid'] = context['active_dialog'].cv.uuid
        else:
            context['opponent_uuid'] = self.action_interview.action.pipeline.vacancy.uuid

        context['ws_server_path'] = '{}://{}:{}/'.format(
            settings.CHAT_WS_SERVER_PROTOCOL,
            settings.CHAT_WS_SERVER_HOST,
            settings.CHAT_WS_SERVER_PORT,
        )
        return context

    def post(self, request, *args, **kwargs):
        self.interview.closed = True
        self.interview.type = request.POST.get('type')
        self.interview.save()
        return super().get(request, *args, **kwargs)

    def check_interview(self, request, *args, **kwargs):
        vac = self.action_interview.action.pipeline.vacancy
        if vac.employer != self.request.role_object and self.interview.cv.candidate != self.request.role_object:
            raise Http404
        if request.method == 'POST':
            vac_uuid = request.POST.get('vac_uuid')
            cv_uuid = request.POST.get('cv_uuid')
            if vac.uuid != vac_uuid or self.interview.cv.uuid != cv_uuid:
                raise Http404
        return super().dispatch(request, *args, **kwargs)


class NewInterviewerView(OnlyEmployerMixin, CreateView):
    model = ActionInterview
    fields = ('action', 'interviewer', )

    def get_success_url(self):
        return reverse('vacancy', kwargs={'pk': self.object.action.pipeline.vacancy.id})

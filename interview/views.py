from datetime import datetime, timedelta

import date_converter
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from interview.forms import ActionInterviewForm, ScheduleMeetingForm
from interview.models import ActionInterview, ScheduledMeeting, InterviewPassed
from pipeline.models import Action
from .zoomus import ZoomusApi


class NewActionInterviewView(CreateView):
    template_name = 'interview/action_interview_new.html'
    form_class = ActionInterviewForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = None

    def dispatch(self, request, *args, **kwargs):
        self.action = get_object_or_404(Action, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial.update({'company': self.action.pipeline.vacancy.company})
        return initial

    def form_valid(self, form):
        form.instance.action = self.action
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('action_details', kwargs={'pk': self.action.pk})


class CandidateInterviewScheduleView(CreateView):
    form_class = ScheduleMeetingForm

    template_name = 'interview/schedule.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.date = None
        self.action_interview = None
        self.candidate = None
        self.meeting = None
        self.employer = None

    def get_initial(self):
        self.employer = self.action_interview.employer
        meetings = ScheduledMeeting.objects.filter(
            action_interview__action__pipeline__vacancy__company__employer=self.employer,
            date__gte=self.date,
            date__lt=self.date + timedelta(days=1)).order_by('time')
        duration = self.action_interview.duration
        a = []
        time_n = None
        find = False
        for item in meetings:
            bla = datetime.now()
            bla = bla.replace(hour=item.time.hour, minute=item.time.minute, second=0)
            if bla >= datetime.now() - timedelta(minutes=duration):
                a.append(item)
        if a:
            next_far = datetime.now()
            next_far = next_far.replace(hour=a[0].time.hour, minute=a[0].time.minute)
            if next_far > datetime.now() + timedelta(minutes=duration):
                time_n = datetime.now()
                find = True
        if not find:
            for i in range(len(a) - 1):
                if a[i].time.replace(minute=a[i].time.minute + duration) < a[i + 1].time:
                    time_n = a[i].time.replace(minute=a[i].time.minute + duration)
                    find = True
        if not find and a:
            next_applied = datetime.now()
            next_applied = next_applied.replace(hour=a[-1].time.hour, minute=a[-1].time.minute, second=0) + timedelta(
                minutes=duration)
            time_n = next_applied
            find = True
        if not find:
            time_n = datetime.now()
        return {'date': self.date, 'time': time_n}

    def get_success_url(self):
        return reverse('candidate_interviewing', kwargs={'pk': self.action_interview.pk})

    def dispatch(self, request, *args, **kwargs):
        self.action_interview = get_object_or_404(ActionInterview, pk=kwargs.get('pk'))
        if 'date' not in request.POST:
            self.date = datetime.now()
        else:
            self.date = date_converter.string_to_datetime(request.POST.get('date'), '%Y-%m-%d')
        if self.action_interview.end_date:
            if datetime.combine(self.action_interview.end_date, datetime.max.time()) < datetime.now():
                messages.warning(request, 'Interview period is over.')
                return HttpResponseRedirect(
                    reverse('vacancy', kwargs={'pk': self.action_interview.action.pipeline.vacancy.id}))
        self.candidate = request.role_object
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_interview'] = self.action_interview
        try:
            passed = InterviewPassed.objects.get(interview=self.action_interview, candidate=self.candidate)
        except InterviewPassed.DoesNotExist:
            try:
                self.meeting = ScheduledMeeting.objects.get(action_interview=self.action_interview,
                                                            candidate=self.candidate)
            except ScheduledMeeting.DoesNotExist:
                self.meeting = None
            context.update({'meeting': self.meeting})
        else:
            context.update({'passed': passed})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'data' in kwargs:
            data = kwargs['data'].copy()
            data.update({'employer': self.employer})
            data.update({'action_interview': self.action_interview})
            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        form.instance.action_interview = self.action_interview
        form.instance.candidate = self.candidate
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']
        zoom = ZoomusApi(settings.ZOOMUS_API_KEY, settings.ZOOMUS_API_SECRET, settings.ZOOMUS_USER_ID)
        try:
            scheduled = zoom.schedule_meeting(topic='Vacancy {} interview'.format(self.action_interview.vacancy.title),
                                              start_time='{}T{}'.format(date, time),
                                              duration=self.action_interview.duration,
                                              timezone=settings.TIME_ZONE)
        except ValueError:
            messages.error(self.request, 'Error during scheduling meeting')
            return super().form_invalid(form)
        else:
            res = scheduled.json()
            form.instance.link_start = res['start_url']
            form.instance.link_join = res['join_url']
            form.instance.conf_id = res['id']
            form.instance.uuid = res['uuid']
            return super().form_valid(form)

from datetime import datetime, timedelta

import date_converter
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from interview.forms import ActionInterviewForm, ScheduleMeetingForm
from interview.models import ActionInterview, ScheduledMeeting, InterviewPassed
from interview.utils import get_first_available_time
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
        if not form.cleaned_data['end_date']:
            form.instance.end_date = form.instance.start_date + timedelta(weeks=settings.DEFAULT_INTERVIEW_END_DATE)
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
        self.recruiters = None
        self.interview_is_over = False

    def dispatch(self, request, *args, **kwargs):
        self.action_interview = get_object_or_404(ActionInterview, pk=kwargs.get('pk'))
        self.recruiters = self.action_interview.recruiters.all()
        self.candidate = request.user

        return self.set_datetime(request, *args, **kwargs)

    def set_datetime(self, request, *args, **kwargs):
        if 'date' in request.POST:
            selected = '{} {}'.format(request.POST.get('date'), request.POST.get('time'))
            date = date_converter.string_to_datetime(selected, '%Y-%m-%d %H:%M')
        else:
            date = datetime.now()

        if self.action_interview.end_time and date.time() > self.action_interview.end_time:
            date = date + timedelta(days=1)

        if date.time() < self.action_interview.start_time or date.time() > self.action_interview.end_time:
            date = date.replace(hour=self.action_interview.start_time.hour,
                                minute=self.action_interview.start_time.minute)

        if self.action_interview.end_date and date.date() > self.action_interview.end_date:
            self.interview_is_over = True

        self.date = date.replace(second=0, microsecond=0)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.interview_is_over:
            messages.info(request, 'Interview time is over')
        if not self.recruiters.exists():
            messages.info(request, 'There is no recruiters for this interview')
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        times = {}
        meetings = ScheduledMeeting.objects.filter(
            action_interview__recruiters__in=self.recruiters,
            date__gte=self.date,
            date__lt=self.date + timedelta(days=1),
            time__gt=self.date.time()).distinct().order_by('time')

        if not meetings:
            return {'date': self.date, 'time': self.date}

        for recruiter in self.recruiters:
            this_day_rec_meetings = recruiter.recruiter_scheduled_meetings.filter(date__gte=self.date,
                                                                                  date__lt=self.date + timedelta(
                                                                                      days=1))
            if not this_day_rec_meetings.exists():
                return {'date': self.date, 'time': self.date}

            for meeting in this_day_rec_meetings:
                if recruiter.id not in times.keys():
                    times[recruiter.id] = []
                times[recruiter.id].append(datetime.combine(meeting.date, meeting.time))

        if times:
            ava_time = []
            for item in times.values():
                r_time = get_first_available_time(item, self.action_interview.duration)
                if r_time:
                    ava_time.append(r_time)
            if ava_time:
                min_time = min(ava_time)
                return {'date': min_time.date(), 'time': min_time.time()}

    def get_success_url(self):
        return reverse('candidate_interviewing', kwargs={'pk': self.action_interview.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_interview'] = self.action_interview
        context['unavailable'] = self.interview_is_over or not self.recruiters
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
            data.update({'recruiters': self.recruiters})
            data.update({'action_interview': self.action_interview})
            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        from interview.utils import get_recruiter_for_time
        form.instance.action_interview = self.action_interview
        form.instance.candidate = self.candidate
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']
        recruiter = get_recruiter_for_time(self.recruiters, datetime.combine(date, time),
                                           self.action_interview.duration)
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
            form.instance.recruiter = recruiter
            return super().form_valid(form)

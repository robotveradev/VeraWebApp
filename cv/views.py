import os

from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, RedirectView, DetailView, CreateView, UpdateView
from web3 import Web3

from jobboard.mixins import OnlyCandidateMixin
from statistic.decorators import statistical
from vacancy.models import VacancyOffer
from .forms import *


class VacancyOfferView(OnlyCandidateMixin, TemplateView):
    template_name = 'cv/vacancy_offer.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['vac_offers'] = VacancyOffer.objects.filter(cv__candidate=request.role_object, is_active=True).order_by(
            '-created_at')
        return self.render_to_response(context)


class CvView(DetailView):

    @method_decorator(statistical)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    model = CurriculumVitae
    template_name = 'cv/cv_full.html'
    context_object_name = 'cv'


class NewCvView(OnlyCandidateMixin, CreateView):
    model = CurriculumVitae
    form_class = CurriculumVitaeForm
    template_name = 'cv/cv_new.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
        self.request = None

    def get_initial(self):
        return {'first_name': self.request.role_object.first_name,
                'last_name': self.request.role_object.last_name,
                'middle_name': self.request.role_object.middle_name}

    def form_valid(self, form):
        form.instance.candidate = self.request.role_object
        form.instance.uuid = Web3.toHex(os.urandom(15))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cv', kwargs={'pk': self.object.pk})


class NewCVFragmentMixin:

    def __init__(self):
        self.cv = None
        self.object = None

    def dispatch(self, request, *args, **kwargs):
        self.cv = get_object_or_404(CurriculumVitae, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cv'] = self.cv
        return context


class NewPositionView(NewCVFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'cv/new_position.html'

    def form_valid(self, form):
        self.object = form.save()
        self.cv.position = self.object
        self.cv.published = True
        self.cv.save()
        return HttpResponseRedirect(reverse('cv', kwargs={'pk': self.cv.id}))


class NewEducationView(NewCVFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'cv/new_education.html'

    def form_valid(self, form):
        self.object = form.save()
        self.cv.education.add(self.object)
        self.cv.save()
        return HttpResponseRedirect(reverse('cv', kwargs={'pk': self.cv.id}))


class NewExperienceView(NewCVFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'cv/new_experience.html'

    def form_valid(self, form):
        self.object = form.save()
        self.cv.experience.add(self.object)
        self.cv.save()
        return HttpResponseRedirect(reverse('cv', kwargs={'pk': self.cv.id}))


class ChangeCvStatusView(OnlyCandidateMixin, RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cv = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('cv', kwargs={'pk': kwargs.get('pk')})

    def get(self, request, *args, **kwargs):
        self.cv = get_object_or_404(CurriculumVitae, pk=kwargs.get('pk'), candidate=request.role_object)
        if not self.cv.position:
            messages.error(request, 'You cannot enable Curriculum Vitae without position.')
        else:
            self.cv.enabled = not self.cv.enabled
            self.cv.save()
        return super().get(request, *args, **kwargs)


class CvAllView(OnlyCandidateMixin, TemplateView):
    template_name = 'cv/cv_all.html'


class CvEditView(OnlyCandidateMixin, UpdateView):
    model = CurriculumVitae
    form_class = CurriculumVitaeForm
    template_name = 'cv/cv_edit.html'

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.candidate != self.request.role_object:
            raise Http404
        return obj


class CvFragmentEditMixin(OnlyCandidateMixin):

    def get_object(self):
        obj = super().get_object()
        if obj.curriculumvitae_set.first().candidate != self.request.role_object:
            raise Http404
        return obj


class PositionEditView(CvFragmentEditMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'cv/position_edit.html'


class ExperienceEditView(CvFragmentEditMixin, UpdateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'cv/experience_edit.html'


class EducationEditView(CvFragmentEditMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'cv/education_edit.html'


class HideOfferView(OnlyCandidateMixin, RedirectView):
    pattern_name = 'offers'

    def get_redirect_url(self, *args, **kwargs):
        offer_o = get_object_or_404(VacancyOffer, id=kwargs['pk'], cv__candidate=self.request.role_object)
        offer_o.refuse()
        return super().get_redirect_url()

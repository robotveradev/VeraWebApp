import os
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView, CreateView, UpdateView
from web3 import Web3

from google_address.models import Address
from jobboard.mixins import OnlyCandidateMixin
from vacancy.models import VacancyOffer
from .forms import *


class VacancyOfferView(OnlyCandidateMixin, TemplateView):
    template_name = 'candidateprofile/vacancy_offer.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['vac_offers'] = VacancyOffer.objects.filter(cv__candidate=request.role_object, is_active=True).order_by(
            '-created_at')
        return self.render_to_response(context)


class NewCVFragmentMixin:
    def __init__(self):
        self.cp = None
        self.object = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cp = CandidateProfile.objects.get(candidate=request.role_object)
        except CandidateProfile.DoesNotExist:
            return redirect(reverse('complete_profile'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cp'] = self.cp
        return context


class NewPositionView(NewCVFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'candidateprofile/new_position.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.cp
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('profile'))


class NewEducationView(NewCVFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'candidateprofile/new_education.html'

    def form_valid(self, form):
        self.object = form.save()
        self.cp.education.add(self.object)
        self.cp.save()
        return HttpResponseRedirect(reverse('profile'))


class NewExperienceView(NewCVFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'candidateprofile/new_experience.html'

    def form_valid(self, form):
        self.object = form.save()
        self.cp.experience.add(self.object)
        self.cp.save()
        return HttpResponseRedirect(reverse('profile'))


class CvEditView(OnlyCandidateMixin, UpdateView):
    model = CandidateProfile
    form_class = CandidateProfileForm
    template_name = 'candidateprofile/cv_edit.html'

    def get_object(self, queryset=None):
        return self.request.role_object.profile


class CvFragmentEditMixin(OnlyCandidateMixin):

    def get_object(self):
        obj = super().get_object()
        if obj.candidateprofile_set.first().candidate != self.request.role_object:
            raise Http404
        return obj


class PositionEditView(CvFragmentEditMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'candidateprofile/position_edit.html'

    def get_object(self, **kwargs):
        return self.request.role_object.profile.position


class ExperienceEditView(CvFragmentEditMixin, UpdateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'candidateprofile/experience_edit.html'


class EducationEditView(CvFragmentEditMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'candidateprofile/education_edit.html'


class HideOfferView(OnlyCandidateMixin, RedirectView):
    pattern_name = 'offers'

    def get_redirect_url(self, *args, **kwargs):
        offer_o = get_object_or_404(VacancyOffer, id=kwargs['pk'], cv__candidate=self.request.role_object)
        offer_o.refuse()
        return super().get_redirect_url()


class CompleteProfileView(OnlyCandidateMixin, CreateView):
    form_class = CandidateProfileForm
    template_name = 'candidateprofile/cp_new.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
        self.request = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            address = Address.objects.create(raw=kwargs['data']['address'])
            data = kwargs['data'].copy()
            data['address'] = address.id
            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        form.instance.candidate = self.request.role_object
        form.instance.uuid = Web3.toHex(os.urandom(15))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile')

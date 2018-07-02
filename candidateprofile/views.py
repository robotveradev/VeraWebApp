import os

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, RedirectView, CreateView, UpdateView
from web3 import Web3

from candidateprofile.tasks import change_candidate_status
from google_address.models import Address
from jobboard.forms import AchievementForm
from jobboard.handlers.oracle import OracleHandler
from jobboard.mixins import OnlyCandidateMixin
from vacancy.models import VacancyOffer, Vacancy
from .forms import *


class VacancyOfferView(OnlyCandidateMixin, TemplateView):
    template_name = 'candidateprofile/vacancy_offer.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['vac_offers'] = VacancyOffer.objects.filter(profile__candidate=request.role_object,
                                                            is_active=True).order_by(
            '-created_at')
        return self.render_to_response(context)


class NewProfileFragmentMixin:
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


class NewPositionView(NewProfileFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'candidateprofile/new_position.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.cp
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('profile'))


class NewEducationView(NewProfileFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'candidateprofile/new_education.html'

    def form_valid(self, form):
        self.object = form.save()
        self.cp.education.add(self.object)
        self.cp.save()
        return HttpResponseRedirect(reverse('profile'))


class NewExperienceView(NewProfileFragmentMixin, OnlyCandidateMixin, CreateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'candidateprofile/new_experience.html'

    def form_valid(self, form):
        self.object = form.save()
        self.cp.experience.add(self.object)
        self.cp.save()
        return HttpResponseRedirect(reverse('profile'))


class ProfileEditView(OnlyCandidateMixin, UpdateView):
    model = CandidateProfile
    form_class = CandidateProfileForm
    template_name = 'candidateprofile/cp_edit.html'

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
        offer_o = get_object_or_404(VacancyOffer, id=kwargs['pk'], profile__candidate=self.request.role_object)
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
        form.instance.uuid = Web3.toHex(os.urandom(32))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile')


class NewLanguageView(OnlyCandidateMixin, CreateView):
    form_class = LanguageItemForm

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        form.instance.profile = self.request.role_object.profile
        return super().form_valid(form)


class NewCitizenshipView(OnlyCandidateMixin, CreateView):
    form_class = CitizenshipForm

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        form.instance.profile = self.request.role_object.profile
        return super().form_valid(form)


class NewWorkPermitView(OnlyCandidateMixin, CreateView):
    form_class = WorkPermitForm

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        form.instance.profile = self.request.role_object.profile
        return super().form_valid(form)


class ChangeStatusView(OnlyCandidateMixin, RedirectView):

    def post(self, request, *args, **kwargs):
        oracle = OracleHandler()
        old_status = oracle.candidate_status(request.role_object.contract_address, only_index=True)
        new_status = request.POST.get('status')
        if new_status != old_status:
            change_candidate_status.delay(request.role_object.id, new_status)
        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('profile')


class CandidateVacanciesView(OnlyCandidateMixin, TemplateView):
    template_name = 'candidateprofile/vacancies.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vac_set = set()
        oracle = OracleHandler()
        count = oracle.candidate_vacancies_length(self.request.role_object.contract_address)
        for i in range(count):
            vac_uuid = oracle.candidate_vacancy_by_index(self.request.role_object.contract_address, i)
            vac_set.add(vac_uuid)
        vacancies = Vacancy.objects.filter(uuid__in=vac_set)
        context.update({'vacancies': vacancies})
        return context


class NewAchievementView(OnlyCandidateMixin, CreateView):
    form_class = AchievementForm
    template_name = 'candidateprofile/new_achievement.html'
    success_url = reverse_lazy('profile')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def form_valid(self, form):
        form.instance.candidate = self.request.role_object
        return super().form_valid(form)

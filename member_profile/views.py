from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, RedirectView, CreateView, UpdateView

from company.models import RequestToCompany
from google_address.models import Address
from jobboard.forms import AchievementForm
from jobboard.handlers.oracle import OracleHandler
from member_profile.tasks import change_candidate_status
from vacancy.models import VacancyOffer
from .forms import *


class VacancyOfferView(TemplateView):
    template_name = 'member_profile/vacancy_offer.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'vac_offers', VacancyOffer.objects.filter(member=self.request.user,
                                                              is_active=True).order_by('-created_at')})


class NewProfileFragmentMixin:
    def __init__(self):
        self.object = None
        self.request = None

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect(reverse('complete_profile'))
        return super().dispatch(request, *args, **kwargs)


class NewPositionView(NewProfileFragmentMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'member_profile/new_position.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.request.user.profile
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse('profile'))


class NewEducationView(NewProfileFragmentMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'member_profile/new_education.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.request.user.profile
        self.object.save()
        return HttpResponseRedirect(reverse('profile'))


class NewAdditionalEducationView(NewProfileFragmentMixin, CreateView):
    model = AdditionalEducation
    form_class = AdditionalEducationForm
    template_name = 'member_profile/new_additional_education.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.request.user.profile
        self.object.save()
        print(self.object)
        return HttpResponseRedirect(reverse('profile'))


class NewExperienceView(NewProfileFragmentMixin, CreateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'member_profile/new_experience.html'

    def process_request(self):
        organization_id = self.request.POST.get('organization_id')
        if organization_id:
            try:
                RequestToCompany.objects.create(company_id=organization_id, member=self.request.user)
            except IntegrityError:
                pass

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = self.request.user.profile
        self.object.save()
        if self.object.still:
            self.process_request()
        return HttpResponseRedirect(reverse('profile'))


class ProfileEditView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'member_profile/cp_edit.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileFragmentEditMixin:

    def __init__(self):
        self.object = None
        self.request = None

    def get_object(self):
        obj = super().get_object()
        if obj.profile.member != self.request.user:
            raise Http404
        return obj


class PositionEditView(ProfileFragmentEditMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'member_profile/position_edit.html'

    def get_object(self, **kwargs):
        return self.request.user.profile.position


class ExperienceEditView(ProfileFragmentEditMixin, UpdateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'member_profile/experience_edit.html'


class EducationEditView(ProfileFragmentEditMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'member_profile/education_edit.html'


class AdditionalEducationEditView(ProfileFragmentEditMixin, UpdateView):
    model = AdditionalEducation
    form_class = AdditionalEducationForm
    template_name = 'member_profile/additional_education_edit.html'


class HideOfferView(RedirectView):
    pattern_name = 'offers'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_redirect_url(self, *args, **kwargs):
        offer_o = get_object_or_404(VacancyOffer, id=kwargs['pk'], member=self.request.user)
        offer_o.refuse()
        return super().get_redirect_url()


class CompleteProfileView(CreateView):
    form_class = ProfileForm
    template_name = 'member_profile/profile_new.html'

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
        form.instance.member = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile')


class NewLanguageView(CreateView):
    form_class = LanguageItemForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class NewCitizenshipView(CreateView):
    form_class = CitizenshipForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class NewWorkPermitView(CreateView):
    form_class = WorkPermitForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class ChangeStatusView(RedirectView):

    def post(self, request, *args, **kwargs):
        oracle = OracleHandler()
        old_status = oracle.candidate_status(request.role_object.contract_address, only_index=True)
        new_status = request.POST.get('status')
        if new_status != old_status:
            change_candidate_status.delay(request.role_object.id, new_status)
        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('profile')


class MemberVacanciesView(TemplateView):
    template_name = 'member_profile/vacancies.html'


class NewAchievementView(NewProfileFragmentMixin, CreateView):
    form_class = AchievementForm
    template_name = 'member_profile/new_achievement.html'
    success_url = reverse_lazy('profile')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)

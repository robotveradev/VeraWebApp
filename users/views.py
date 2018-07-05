from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView

from users.models import InviteCode
from .forms import SendPhoneVerificationForm, PhoneVerificationForm
from .utils import send_verfication_code, verify_sent_code


class PhoneVerifyView(FormView):
    template_name = 'users/send_phone_verify.html'
    form_class = SendPhoneVerificationForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def get_initial(self):
        return {
            'phone_number': self.request.user.phone_number,
            'country_code': self.request.user.country_code,
            'via': 'sms'
        }

    def dispatch(self, request, *args, **kwargs):
        if request.user.phone_number_verified:
            messages.info(request, 'Phone number was confirmed earlier')
            return HttpResponseRedirect(reverse('profile'))
        return super().dispatch(request, *args, **kwargs)

    def check_user_phone(self, form):
        if form.cleaned_data['phone_number'] != self.request.user.phone_number:
            self.request.user.phone_number = form.cleaned_data['phone_number']
        if form.cleaned_data['country_code'] != self.request.user.country_code:
            self.request.user.country_code = form.cleaned_data['country_code']
        self.request.user.save()

    def form_valid(self, form):
        self.check_user_phone(form)
        result = send_verfication_code(**form.cleaned_data)
        if result['success']:
            messages.info(self.request, result['message'])
            return HttpResponseRedirect(reverse('verify_code'))
        messages.info(self.request, result['message'])
        return super().form_invalid(form)


class VerifyCode(FormView):
    template_name = 'users/verify_phone.html'
    form_class = PhoneVerificationForm
    success_url = reverse_lazy('profile')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def form_valid(self, form):
        result = verify_sent_code(form.cleaned_data['one_time_password'],
                                  self.request.user)
        if result['success']:
            messages.info(self.request, 'Phone number verified successfully')
            self.request.user.phone_number_verified = True
            self.request.user.save()
            return super().form_valid(form)
        messages.error(self.request, result['message'])
        return super().form_invalid(form)


class InviteView(RedirectView):

    def dispatch(self, request, *args, **kwargs):
        if not request.session.session_key:
            request.session.save()
        invite_object = get_object_or_404(InviteCode, code=kwargs.get('code'), expired=False)
        if invite_object.one_off:
            invite_object.expired = True
            invite_object.session_key = request.session.session_key
        else:
            invite_object.session_key = 'all'
        invite_object.save()
        hrr = HttpResponseRedirect(reverse('account_signup'))
        hrr.set_cookie('invitetoken', invite_object.code)
        return hrr


def handler404(request):
    response = render_to_response('404.html',
                                  context=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html',
                                  context=RequestContext(request))
    response.status_code = 500
    return response

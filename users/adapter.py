from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email
from django.conf import settings
from django.contrib import messages

from users.models import InviteCode


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        from allauth.account.utils import user_field

        data = form.cleaned_data
        phone_number = data.get('phone_number')
        country_code = data.get('country_code')
        if phone_number:
            user_field(user, 'phone_number', phone_number)
        if country_code:
            user_field(user, 'country_code', country_code)
        return super().save_user(request, user, form, commit)

    def is_open_for_signup(self, request):
        if not hasattr(settings, 'ACCOUNT_OPEN_SIGNUP') or settings.ACCOUNT_OPEN_SIGNUP:
            return True

        invtoken = request.COOKIES.get('invitetoken')
        sess_key = request.COOKIES.get('sessionid')
        try:
            invite_object = InviteCode.objects.get(code=invtoken)
        except InviteCode.DoesNotExist:
            return False
        else:
            if invite_object.used_by is not None:
                return False
            if invite_object.one_off:
                if not invite_object.expired or invite_object.session_key != sess_key:
                    return False
            return True

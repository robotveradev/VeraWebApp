from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from users.models import InviteCode


@receiver(user_signed_up)
def user_signup(request, user, **kwargs):
    invtoken = request.COOKIES.get('invitetoken')
    sess_key = request.COOKIES.get('sessionid')

    try:
        invite_object = InviteCode.objects.get(code=invtoken,
                                               session_key=sess_key,
                                               expired=True)
    except:
        pass
    else:
        invite_object.used_by = user
        invite_object.save()

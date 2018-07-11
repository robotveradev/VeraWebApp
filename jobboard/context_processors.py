from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from jobboard.models import Transaction


def roles(request):
    ctx = {
        "role": request.role,
        "role_object": request.role_object,
    }
    return ctx


def hints(request):
    ctx = {
        "hints_enabled": settings.HINTS_ENABLED,
    }
    return ctx


def txns(request):
    ctx = {}
    if not isinstance(request.user, AnonymousUser):
        ctx.update({
            'txns': Transaction.objects.filter(user=request.user)
        })
    return ctx

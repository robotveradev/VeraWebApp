from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from jobboard.models import Transaction


def hints(request):
    ctx = {
        "hints_enabled": settings.HINTS_ENABLED,
    }
    return ctx


def txns(request):
    ctx = {}
    if not isinstance(request.user, AnonymousUser):
        ctx.update({
            'txns': Transaction.objects.filter(user=request.user.id)
        })
    return ctx

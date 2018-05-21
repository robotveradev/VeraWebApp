from __future__ import unicode_literals

from django.conf import settings


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

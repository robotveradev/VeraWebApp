from __future__ import unicode_literals
import functools
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import available_attrs
from account.compat import is_authenticated


def choose_role_required(func=None):
    """
    Decorator for views that checks that the user choose his role, redirecting
    to the choose page if necessary.
    """

    def decorator(view_func):
        @functools.wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not is_authenticated(request.user) or request.role is None:
                return HttpResponseRedirect(reverse('choose_role'))
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if func:
        return decorator(func)
    return decorator


def role_required(argument):
    def real_decorator(view_func):
        @functools.wraps(view_func, assigned=available_attrs(view_func))
        def wrapper(request, *args, **kwargs):
            if request.role_object.__class__.__name__.lower() != argument.lower():
                return HttpResponse(status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return real_decorator

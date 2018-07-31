from __future__ import unicode_literals
import functools
from django.db import transaction
from django.urls import resolve, Resolver404, NoReverseMatch
from django.contrib.contenttypes.models import ContentType


def statistical(f):
    @functools.wraps(f)
    def decorator(request, *args, **kwargs):
        ip = get_client_ip(request)
        user_id = request.user.id or None
        if not request.session.session_key:
            request.session.save()
        try:
            statistic_object = resolve(request.get_full_path()).url_name
        except (Resolver404, NoReverseMatch):
            pass
        else:
            try:
                model_object = ContentType.objects.get(app_label='statistic', model=statistic_object + 'statistic')
            except ContentType.DoesNotExist:
                pass
            else:
                with transaction.atomic():
                    obj, cr = model_object.model_class().objects.get_or_create(role='Member',
                                                                               role_obj_id=user_id,
                                                                               ip=ip,
                                                                               session_id=request.session.session_key,
                                                                               obj_id=kwargs.get('pk'))
                    if not cr:
                        obj.update_count()
                        obj.save()

        return f(request, *args, **kwargs)

    return decorator


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

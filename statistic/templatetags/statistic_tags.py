from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone

register = template.Library()

CORRECT_NAME = {'curriculumvitae': 'cv'}


@register.inclusion_tag('statistic/tags/statistic.html', takes_context=True)
def statistic(context, item, show_type='short'):
    statistic_set = None
    model_name = CORRECT_NAME.get(item.__class__.__name__.lower(), item.__class__.__name__.lower())
    try:
        statistic_object = ContentType.objects.get(app_label='statistic',
                                                   model=model_name + 'statistic')
    except ContentType.DoesNotExist:
        pass
    else:
        statistic_set = statistic_object.model_class().objects.filter(obj_id=item.id).exclude(
            role=context.request.role,
            role_obj_id=context.request.role_object.id)
    return {'statistic': statistic_set,
            'show_type': show_type,
            'empty': not statistic_set.exists(),
            'item': item}


@register.inclusion_tag('statistic/tags/statistic_short.html')
def statistic_short(statistic_set, item):
    context = {'item': item}
    replaced_to_day_start_date = timezone.now().replace(hour=0, minute=0, second=0)
    per_day = statistic_set.filter(date_created__gte=replaced_to_day_start_date)
    per_month = statistic_set.filter(date_created__gte=replaced_to_day_start_date.replace(day=1))
    context['all'] = statistic_set.aggregate(sum=Sum('count'))['sum']
    context['per_day'] = per_day.aggregate(sum=Sum('count'))['sum']
    context['per_month'] = per_month.aggregate(sum=Sum('count'))['sum']
    context['unique'] = statistic_set.count()
    context['unique_per_day'] = per_day.count()
    context['unique_per_month'] = per_month.count()
    return context


@register.filter(name='user_role')
def user_role(statistic_object):
    try:
        model_obj = ContentType.objects.get(app_label='jobboard', model=statistic_object.role.lower())
    except ContentType.DoesNotExist:
        return None
    else:
        try:
            role_obj = model_obj.model_class().objects.get(pk=statistic_object.role_obj_id)
        except model_obj.model_class().DoesNotExist:
            return None
        else:
            return {
                'role': role_obj.__class__.__name__,
                'obj': role_obj
            }

from django import template

register = template.Library()


@register.inclusion_tag('vacancy/tags/job_with_count.html')
def get_jobs_with(item, type_s, vacancies_list):
    if type_s == 'spec':
        count = vacancies_list.filter(specializations__in=[item, ]).count()
    elif type_s == 'keyword':
        count = vacancies_list.filter(keywords__in=[item, ]).count()
    elif type_s == 'salary':
        count = vacancies_list.filter(salary_from__gte=item).count()
    elif type_s == 'busyness':
        count = vacancies_list.filter(busyness__in=[item, ]).count()
    elif type_s == 'schedule':
        count = vacancies_list.filter(schedule__in=[item, ]).count()
    return {'count': count}


@register.filter(name='get_filter_url')
def get_filter_url(get_dict, item):
    need_key = item.__class__.__name__.lower()
    query_str = '?'
    query_list = ['{}={}'.format(need_key, item.pk)]
    for key, value in get_dict.items():
        if key == need_key:
            pass
        else:
            query_list.append('{}={}'.format(key, value))
    query_str += '&'.join(query_list)
    return query_str


@register.filter(name='get_salary_url')
def get_salary_url(get_dict, salary):
    query_str = '?'
    query_list = ['salary={}'.format(salary)]
    for key, value in get_dict.items():
        if key == 'salary':
            pass
        else:
            query_list.append('{}={}'.format(key, value))
    query_str += '&'.join(query_list)
    return query_str


@register.filter(name='get_custom_url')
def get_custom_url(get_dict, item):
    query_str = '?'
    query_list = ['{}={}'.format(item['type'], item['id'])]
    for key, value in get_dict.items():
        if key == item['type']:
            pass
        else:
            query_list.append('{}={}'.format(key, value))
    query_str += '&'.join(query_list)
    return query_str


@register.filter(name='get_clear_url')
def get_clear_url(get_dict, item):
    if len(get_dict) > 0:
        query_str = '?'
        query_list = []
        if not isinstance(item, str):
            need_key = item.__class__.__name__.lower()
            for key, value in get_dict.items():
                if key == need_key:
                    pass
                else:
                    query_list.append('{}={}'.format(key, value))
        else:
            for key, value in get_dict.items():
                if key == item:
                    pass
                else:
                    query_list.append('{}={}'.format(key, value))
        query_str += '&'.join(query_list)
        return query_str
    else:
        return ''

from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Transaction
from pipeline.models import Action, ActionType
from users.models import Member
from vacancy.models import Vacancy

register = template.Library()


@register.filter(name='resort_pipeline')
def resort_pipeline(actions, size):
    arrs = []
    while len(actions) > size:
        piece = actions[:size]
        arrs.append(piece)
        actions = actions[size:]
    arrs.append(actions)
    return {'resorted': arrs, 'count': range(len(arrs))}


def get_action(pipeline, index):
    try:
        action = Action.objects.get(pipeline=pipeline, sort=index)
    except Action.DoesNotExist:
        return None
    else:
        return action


@register.filter
def vacancy_by_uuid(vac_uuid):
    try:
        return Vacancy.objects.get(uuid=vac_uuid)
    except Vacancy.DoesNotExist:
        return None


@register.filter
def pipeline_max_length(a=None):
    oracle = OracleHandler()
    return oracle.pipeline_max_length


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def question_result(answers, question_id):
    context = []
    try:
        ans = answers['question_' + str(question_id)]
    except KeyError:
        return context
    else:
        if isinstance(ans, list):
            context = [int(i) for i in ans]
        else:
            try:
                context = [int(ans), ]
            except ValueError:
                context = [ans, ]
        return context


def vacancy_actions(vacancy):
    oracle = OracleHandler()
    pipeline_length = oracle.get_vacancy_pipeline_length(vacancy.company.contract_address, vacancy.uuid)
    actions = [oracle.get_action(vacancy.company.contract_address, vacancy.uuid, i) for i in range(pipeline_length)]
    db_actions = Action.objects.filter(pipeline__vacancy=vacancy)
    res = [{**i, 'db': j} for i in actions for j in db_actions if i['id'] == j.index]
    return res


@register.inclusion_tag('pipeline/employer_pipeline.html', takes_context=True)
def employer_pipeline_for_vacancy(context, vacancy):
    oracle = OracleHandler()
    members_on_action = oracle.get_members_on_vacancy_by_action_count(vacancy.company.contract_address, vacancy.uuid)
    vac_actions = vacancy_actions(vacancy)
    cont_actions = [{**i, 'cans': i['id'] in members_on_action and members_on_action[i['id']] or 0} for i in vac_actions]
    context.update({'actions': cont_actions,
                    'types': ActionType.objects.all()})
    return context


@register.filter
def set_action_status_color(action):
    if action.action_type.condition_of_passage:
        return hasattr(action, action.action_type.condition_of_passage) and 'green' or 'warning'
    return 'green'


@register.filter
def employer_pipeline_action_config_link(action):
    return reverse('action_details', kwargs={'pk': action.id})


@register.inclusion_tag('pipeline/include/actions_handler.html')
def actions_handler(action):
    cond = action['db'].action_type.condition_of_passage
    context = {'type': cond or None, 'action': action}
    if cond:
        if hasattr(action['db'], cond):
            context.update({cond: getattr(action['db'], cond, None)})
    return context


@register.inclusion_tag('pipeline/include/result.html')
def get_result_link(candidate, action):
    context = {}
    cond = action.action_type.condition_of_passage
    if cond is None:
        context['no_action_provided'] = True
    elif hasattr(action, action.action_type.condition_of_passage):
        action_handler = getattr(action, action.action_type.condition_of_passage)
        url = action_handler.get_result_url(candidate_id=candidate.id)
        context['url'] = url
    return context


@register.filter
def blocked(action):
    return Transaction.objects.filter(obj_id=action.id, txn_type='ActionChanged').exists()


@register.filter
def candidates_on_vacancy_count(actions):
    return sum([len(actions['pass']), len(actions['now']), len(actions['rest'])])


@register.inclusion_tag('pipeline/include/candidate_pipeline_for_vacancy.html')
def candidate_pipeline_for_vacancy(vacancy):
    actions = vacancy_actions(vacancy)
    oracle = OracleHandler()
    candidate_current_action_index = oracle.get_candidate_current_action_index(vacancy.uuid, candidate.contract_address)
    if not oracle.candidate_passed(vacancy.uuid, candidate.contract_address):
        return {
            'actions': actions,
            'candidate_current_action_index': candidate_current_action_index,
            'candidate': candidate,
            'vacancy': vacancy
        }
    else:
        return {'pass': True, 'vacancy': vacancy}


@register.filter
def get(arr, i):
    return arr[i]


@register.filter
def get_member(candidate_contract_address):
    try:
        return Member.objects.get(contract_address=candidate_contract_address)
    except Member.DoesNotExist:
        return None


@register.filter
def action_passed(action, candidate):
    cond = action.action_type.condition_of_passage
    if cond is None:
        return False
    if hasattr(action, cond):
        handler = getattr(action, cond)
        try:
            model = ContentType.objects.get(model=cond + 'passed')
        except ContentType.DoesNotExist:
            return False
        else:
            filt = {cond: handler.id}
            return model.model_class().objects.filter(candidate=candidate, **filt).exists()


@register.filter
def vacancy_members(vacancy):
    oracle = OracleHandler()
    members = oracle.get_members_on_vacancy(vacancy.company.contract_address, vacancy.uuid, True, True)
    return members


@register.filter
def passed(candidates):
    return [i for i in candidates if i['passed']]


@register.filter
def on_action(candidates, action_index):
    return [i for i in candidates if i['action_index'] == action_index]


@register.filter
def get_pending_actions_count(vacancy_id):
    return range(Transaction.objects.filter(txn_type='NewAction', vac_id=vacancy_id).count())


@register.filter
def full_payment(actions):
    return sum([i['fee'] for i in actions])


@register.filter
def get_max_candidates_count(allowed, pay):
    try:
        return int(allowed) // int(pay)
    except:
        return 0

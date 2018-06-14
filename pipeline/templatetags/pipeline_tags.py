from django import template
from django.urls import reverse

from interview.forms import ActionInterviewForm
from interview.models import ActionInterview
from jobboard.handlers.oracle import OracleHandler
from pipeline.models import Action
from quiz.models import ExamPassed
from vacancy.models import Vacancy

register = template.Library()


@register.filter(name='resort_pipeline')
def resort_pipeline(actions):
    return actions[:5], actions[5:][::-1]


@register.filter(name='check_action')
def check_action(action, vacancy):
    action = get_action(vacancy.pipeline, action['id'])
    if action is not None:
        return process_action(action)
    return True


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


def process_action(action):
    condition = action.type.condition_of_passage
    if condition is None:
        return True
    elif condition == 'quiz':
        return action.exam.exists()
    elif condition == 'interview':
        return action.interview.exists()


@register.filter
def pipeline_max_length(a=None):
    oracle = OracleHandler()
    return range(oracle.pipeline_max_length)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.inclusion_tag("pipeline/candidate_action_results_link.html")
def results_with_link(action, profile):
    # TODO change for cv -> candidate
    context = {}
    if hasattr(action, 'type'):
        context = {'type': action.type.condition_of_passage}
        if context['type'] == 'quiz':
            try:
                exam_passed = ExamPassed.objects.get(profile=profile, exam__action=action)
            except ExamPassed.DoesNotExist:
                context['not_passed'] = True
                context['message'] = 'Candidate doesnt pass exam yet'
            else:
                context['url'] = exam_passed.get_absolute_url()
                context['exam_passed'] = exam_passed
        elif action.type.condition_of_passage == 'interview':
            action_interview = ActionInterview.objects.get(action=action)
            context['url'] = reverse('interview', kwargs={'pk': action_interview.id, 'cv_id': cv.id})
    return context


@register.filter
def question_result(answers, question_id):
    try:
        context = []
        try:
            context = [int(i) for i in answers['question_' + str(question_id)]]
        except ValueError:
            context.append(answers['question_' + str(question_id)])
        return context
    except KeyError:
        return []


@register.inclusion_tag('pipeline/interview_chooser.html')
def get_interview(action):
    context = {'action': action}
    try:
        action_interview = ActionInterview.objects.get(action=action)
    except ActionInterview.DoesNotExist:
        context['form'] = ActionInterviewForm()
    else:
        context['interview'] = action_interview
    return context


@register.inclusion_tag('pipeline/employer_pipeline.html')
def employer_pipeline_for_vacancy(vacancy):
    oracle = OracleHandler()
    pipeline_length = oracle.get_vacancy_pipeline_length(vacancy.uuid)
    actions = [oracle.get_action(vacancy.uuid, i) for i in range(pipeline_length)]
    return {'actions': actions, 'vacancy': vacancy}

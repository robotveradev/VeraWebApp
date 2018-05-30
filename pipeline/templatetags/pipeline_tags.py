import itertools
from django import template
from django.urls import reverse
from candidateprofile.models import CandidateProfile
from interview.forms import ActionInterviewForm
from interview.models import ActionInterview
from jobboard.handlers.new_oracle import OracleHandler
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
def cv_by_uuid(cv_uuid):
    try:
        return CandidateProfile.objects.get(uuid=cv_uuid)
    except CandidateProfile.DoesNotExist:
        return None


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


@register.filter(name='pipeline_max_length')
def pipeline_max_length(i):
    oracle = OracleHandler()
    return range(oracle.pipeline_max_length - 1)


@register.inclusion_tag('pipeline/line.html')
def vacancy_employer_pipeline(vacancy):
    context = pipeline_context(vacancy)
    return context


@register.filter
def candidate_cvs_on_vacancy(vacancy, candidate):
    cvs = []
    oracle = OracleHandler()
    current_action = oracle.current_cv_action_on_vacancy(vacancy.uuid, candidate.profile.uuid)
    if not is_empty_action(current_action):
        cvs.append({'cv_object': candidate.profile, 'current_action': current_action})
    return cvs


def is_empty_action(action):
    return action['title'] == '' and action['id'] == 0


@register.inclusion_tag('pipeline/candidate_line.html')
def vacancy_candidate_pipeline(vacancy, candidate):
    context = pipeline_context(vacancy)
    context['candidate'] = candidate
    context['cvs'] = candidate_cvs_on_vacancy(vacancy, candidate)
    return context


@register.filter
def cvs_on_vacancy_per_stage(vac_uuid):
    oracle = OracleHandler()
    cvs = oracle.cvs_on_vacancy(vac_uuid)
    cvs_per_stages = {}
    for item in cvs:
        stage = oracle.current_cv_action_on_vacancy(vac_uuid, item)
        if stage['id'] not in cvs_per_stages:
            cvs_per_stages[stage['id']] = []
        cvs_per_stages[stage['id']].append(item)
    return cvs_per_stages


def pipeline_context(vacancy):
    oracle = OracleHandler()
    pipeline = []
    pipeline_len = oracle.get_vacancy_pipeline_length(vacancy.uuid)
    for i in range(pipeline_len):
        action = oracle.get_action(vacancy.uuid, i)
        action.update({'last': action['id'] == pipeline_len - 1})
        action['db_action'] = get_action(vacancy.pipeline, i)
        pipeline.append(action)
    return {'pipeline': pipeline, 'vacancy': vacancy}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_passed_cvs_by(dictionary, key):
    return list(itertools.chain(*[v for k, v in dictionary.items() if k > key]))


@register.inclusion_tag('pipeline/next_action.html')
def next_action_condition(pipeline, cv):
    context = {}
    action = get_action(pipeline, cv['current_action']['id'])
    if action:
        action_type = action.type.condition_of_passage
        context['action'] = action
        context['next_approvable'] = cv['current_action']['approvable']
        if action_type == 'quiz':
            context['url'] = reverse('candidate_examining',
                                     kwargs={'pk': action.exam.first().id, 'cv_id': cv['cv_object'].pk})
        elif action_type == 'interview':
            context['url'] = reverse('interview',
                                     kwargs={'pk': action.interview.first().id, 'cv_id': cv['cv_object'].pk})
    return context


@register.inclusion_tag("pipeline/candidate_action_results_link.html")
def results_with_link(action, cv):
    context = {}
    if hasattr(action, 'type'):
        context = {'type': action.type.condition_of_passage}
        if context['type'] == 'quiz':
            try:
                exam_passed = ExamPassed.objects.get(cv=cv, exam__action=action)
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

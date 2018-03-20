from django import template

from quiz.models import Category, QuestionKind

register = template.Library()


@register.inclusion_tag('quiz/tags/category_list.html')
def category(cat, selected):
    categories = Category.objects.filter(parent_category=cat)
    return {'categories': categories, 'selected': selected}


@register.filter(name='get_right')
def get_right(qs):
    return qs.filter(weight__gt=0)


@register.inclusion_tag('quiz/tags/question_kinds.html')
def get_questions_kinds(question):
    kinds = QuestionKind.objects.all()
    return {'kinds': kinds, 'question': question}


@register.filter(name='is_question_can_be_kind')
def is_question_can_be_kind(question, kind):
    answers_count = question.answers.count()
    if answers_count >= kind.min_answers:
        return True
    return False

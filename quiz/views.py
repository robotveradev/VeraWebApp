from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView
from django.views.generic.edit import BaseUpdateView

from jobboard.handlers.oracle import OracleHandler
from pipeline.models import Action
from quiz.forms import CategoryForm
from quiz.models import ActionExam, Category, Question, Answer, QuestionKind, ExamPassed, AnswerForVerification
from users.models import Member


class ActionExamView(ListView):
    template_name = 'quiz/action_exams.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = None

    def dispatch(self, request, *args, **kwargs):
        self.action = get_object_or_404(Action,
                                        id=kwargs.get('pk'),
                                        pipeline__vacancy__company__employer=request.role_object)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return hasattr(self.action, 'exam') and self.action.exam or None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = self.action
        return context


class ActionAddQuestionsView(ListView):
    template_name = 'quiz/add_exam.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = None
        self.request = None

    def dispatch(self, request, *args, **kwargs):
        self.action = get_object_or_404(Action, id=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Category.objects.filter(company=self.action.pipeline.vacancy.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = self.action
        if hasattr(self.action, 'exam'):
            context['selected'] = self.get_seleted_exam_questions()
        return context

    def get_seleted_exam_questions(self):
        return [qe.id for qe in self.action.exam.questions.all()]

    def post(self, request, *args, **kwargs):
        action = get_object_or_404(Action,
                                   id=request.POST.get('action'))

        question_ids = request.POST.getlist('questions')
        if not question_ids:
            ActionExam.objects.filter(action=action).delete()
            return redirect('action_details', pk=action.id)
        action_exam, _ = ActionExam.objects.get_or_create(action=action)
        action_exam.questions.set(Question.objects.filter(id__in=question_ids))
        action_exam.save()
        return redirect('action_details', pk=action.id)


class CandidateExaminingView(TemplateView):
    template_name = 'quiz/candidate_examining.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action_exam = None
        self.profile = None
        self.request = None
        self.already_pass_exam = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.already_pass_exam:
            context['exam_passed'] = ExamPassed.objects.filter(candidate=self.request.user,
                                                               exam=self.action_exam).first()
        else:
            context['candidate'] = self.request.user
            context['exam'] = self.action_exam
        context['action'] = self.action_exam.action
        return context

    def get(self, request, *args, **kwargs):
        self.action_exam = get_object_or_404(ActionExam, pk=kwargs.get('pk'))
        self.check_candidate()
        return super().get(self, request, *args, **kwargs)

    def check_candidate(self):
        self.already_pass_exam = ExamPassed.objects.filter(candidate=self.request.user,
                                                           exam=self.action_exam).exists()

    def post(self, request, *args, **kwargs):
        self.process_request(request)
        return HttpResponseRedirect(
            reverse('candidate_examining', kwargs={'pk': self.action_exam.pk}))

    def process_request(self, request):
        self.action_exam = get_object_or_404(ActionExam, pk=request.POST.get('exam_id', None))
        answers = {key: value[0] if len(value) == 1 else value for key, value in dict(request.POST).items() if
                   key.startswith('question_') and value[0] != ''}
        ExamPassed.objects.create(candidate=request.user, exam=self.action_exam, answers=answers)


class QuizIndexPage(TemplateView):
    template_name = 'quiz/main.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class NewCategoryView(CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('quiz_index')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['member'] = self.request.user
        return kwargs


class CategoryView(DetailView):
    model = Category


class NewQuestionView(CreateView):
    model = Question
    fields = ['question_text', 'weight', ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cat = None
        self.object = None
        self.next = None

    def get_success_url(self):
        if '_addanother' in self.request.POST:
            return reverse('new_question', kwargs={'category_id': self.cat.id})
        elif '_addanswers' in self.request.POST:
            return reverse('new_answer', kwargs={'question_id': self.object.id})
        return reverse('category', kwargs={'pk': self.cat.id})

    def dispatch(self, request, *args, **kwargs):
        self.cat = get_object_or_404(Category, id=kwargs.get('category_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.category = self.cat
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.cat
        return context


class NewAnswerView(CreateView):
    model = Answer
    fields = ['text', 'weight', ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.question = None
        self.object = None
        self.another = False

    def get_context_data(self, **kwargs):
        kwargs['question'] = self.question
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('category', kwargs={'pk': self.question.category.id})

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, id=kwargs.get('question_id'))
        if '_addanother' in request.POST:
            self.another = True
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.question = self.question
        self.object.save()
        self.set_question_type()
        return HttpResponseRedirect(
            reverse('new_answer', kwargs={'question_id': self.question.id}) if self.another else self.get_success_url())

    def set_question_type(self):
        answers = self.question.answers
        valid_count = answers.filter(weight__gt=0).count()
        all_count = answers.count()
        if all_count == 1:
            if valid_count == 1:
                self.object.question.kind = QuestionKind.objects.get(title='FreeResponseQuestion')
        elif all_count > 1:
            if valid_count == 1:
                self.object.question.kind = QuestionKind.objects.get(title='MultipleChoice')
            elif valid_count > 1:
                self.object.question.kind = QuestionKind.objects.get(title='MultipleResponse')
        self.object.question.save()


class QuestionUpdateKindView(UpdateView):
    model = Question
    fields = ['kind', ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pk = None

    def get_success_url(self):
        return reverse('category', kwargs={'pk': self.pk})

    def post(self, request, *args, **kwargs):
        question_object = get_object_or_404(Question, pk=kwargs.get('pk'))
        self.pk = question_object.category.id
        return super().post(request, *args, **kwargs)


class ExamUpdateGradeView(BaseUpdateView):
    model = ActionExam
    fields = ['passing_grade', ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(True, status=200)

    def form_invalid(self, form):
        return HttpResponse(False, status=400)


class ProcessAnswerView(View):

    def dispatch(self, request, *args, **kwargs):
        if not self.request.is_ajax():
            return HttpResponse(status=403)
        return super(ProcessAnswerView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=request.POST.get('que_id'))
        answer = request.POST.get('ans')
        AnswerForVerification.objects.create(question=question, answer=answer)
        return HttpResponse('ok', status=200)


class ExamPassedView(DetailView):
    model = ExamPassed

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action_exam = None
        self.candidate = None

    def dispatch(self, request, *args, **kwargs):
        self.action_exam = get_object_or_404(ActionExam, pk=kwargs.get('exam_id'))
        if self.action_exam.action.pipeline.vacancy.company not in request.user.companies:
            raise Http404
        self.candidate = get_object_or_404(Member, pk=kwargs.get('candidate_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            results = ExamPassed.objects.get(exam=self.action_exam, candidate=self.candidate)
        except ExamPassed.DoesNotExist:
            results = {}
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = self.action_exam.action
        context['candidate'] = self.candidate
        oracle = OracleHandler()
        vacancy = self.action_exam.action.pipeline.vacancy
        mci = oracle.get_member_current_action_index(vacancy.company.contract_address, vacancy.uuid,
                                                     self.candidate.contract_address)
        mci == self.action_exam.action.index and context.update({'not_yet': True})
        return context


class QuizCompanyPage(TemplateView):
    pass

import time
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView, RedirectView
from django.views.generic.edit import BaseUpdateView
from jobboard.tasks import save_txn_to_history, save_txn
from jobboard.handlers.candidate import CandidateHandler
from jobboard.handlers.oracle import OracleHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.models import Employer
from quiz.forms import CategoryForm
from vacancy.models import Vacancy
from quiz.models import ActionExam, Category, Question, Answer, QuestionKind, ExamPassing, AnswerForVerification


class VacancyExamView(ListView):
    template_name = 'quiz/vacancy_exams.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vacancy = None

    def dispatch(self, request, *args, **kwargs):
        if not isinstance(request.role_object, Employer):
            raise Http404
        self.vacancy = get_object_or_404(Vacancy, id=kwargs.get('vacancy_id'), employer=request.role_object)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.vacancy.tests.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancy'] = self.vacancy
        return context

# TODO переписать под action
class VacancyAddQuestionsView(ListView):
    template_name = 'quiz/add_exam.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vacancy = None

    def dispatch(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, id=kwargs.get('vacancy_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Category.objects.filter(employer=self.request.role_object, parent_category=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancy'] = self.vacancy
        context['selected'] = self.get_seleted_exam_questions()
        return context

    def get_seleted_exam_questions(self):
        exam = ActionExam.objects.filter(action=self.action).first()
        if exam is not None:
            return [qe.id for qe in exam.questions.all()]
        return []

    def post(self, request, *args, **kwargs):
        vacancy = get_object_or_404(Vacancy, employer=request.role_object, id=request.POST.get('vacancy'))
        question_ids = request.POST.getlist('questions')
        vacancy_exam, _ = ActionExam.objects.get_or_create(vacancy=vacancy)
        vacancy_exam.questions.set(Question.objects.filter(id__in=question_ids))
        vacancy_exam.save()
        return redirect('vacancy_exam', vacancy_id=vacancy.id)


class CandidateExaminingView(TemplateView):
    template_name = 'quiz/candidate_examining.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vacancy = None
        self.already_pass_exam = False

    def get(self, request, *args, **kwargs):
        res = self.check_request(**kwargs)
        return res if res else super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.already_pass_exam:
            context['exam_passed'] = ExamPassing.objects.filter(exam__vacancy=self.vacancy,
                                                                candidate=self.request.role_object).first()
        else:
            context['exam'] = ActionExam.objects.filter(vacancy=self.vacancy).first()
        context['vacancy'] = self.vacancy
        return context

    def check_request(self, **kwargs):
        vac = kwargs.get('vacancy_id', None)
        self.vacancy = Vacancy.objects.get(id=vac) if vac is not None else None
        if self.vacancy and self.vacancy.contract_address:
            return self.check_candidate()
        else:
            raise Http404

    def check_candidate(self):
        vac_h = VacancyHandler(settings.WEB_ETH_COINBASE, self.vacancy.contract_address)
        if ExamPassing.objects.filter(candidate=self.request.role_object, exam__vacancy=self.vacancy).count() > 0:
            self.already_pass_exam = True
        state = vac_h.get_candidate_state(self.request.role_object.contract_address)
        if state != 'accepted':
            return HttpResponse(status=403)

    def post(self, request, *args, **kwargs):
        self.process_request(request)
        return HttpResponseRedirect(reverse('profile'))

    @staticmethod
    def process_request(request):
        exam = get_object_or_404(ActionExam, pk=request.POST.get('exam_id', None))
        answers = {key: value[0] if len(value) == 1 else value for key, value in dict(request.POST).items() if
                   key.startswith('question_') and value[0] != ''}
        ExamPassing.objects.create(candidate=request.role_object, exam=exam, answers=answers)


class QuizIndexPage(TemplateView):
    template_name = 'quiz/main.html'

    def get_context_data(self, **kwargs):
        context = super(QuizIndexPage, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(employer=self.request.role_object, parent_category=None)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class NewCategoryView(CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('quiz_index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['employer'] = self.request.role_object
        return kwargs

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.employer = self.request.role_object
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


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
        return HttpResponse(False, status=403)


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


class PayToCandidateView(RedirectView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.candidate = None
        self.vacancy = None
        self.vacancy_handler = None
        self.exam = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('profile')

    def dispatch(self, request, *args, **kwargs):
        self.candidate = request.role_object
        self.vacancy = get_object_or_404(Vacancy, id=kwargs.get('vacancy_id', None))
        self.exam = ActionExam.objects.filter(vacancy=self.vacancy).first()
        return self.check_vacancy_enabled(request, *args, **kwargs)

    def check_vacancy_enabled(self, request, *args, **kwargs):
        if not self.vacancy.enabled:
            return HttpResponse(status=403)
        else:
            self.vacancy_handler = VacancyHandler(settings.WEB_ETH_COINBASE, self.vacancy.contract_address)
        return self.check_the_candidate(request, *args, **kwargs)

    def check_the_candidate(self, request, *args, **kwargs):
        state = self.vacancy_handler.get_candidate_state(self.candidate.contract_address)
        if state != 'accepted':
            return HttpResponse(status=403)
        return self.check_candidate_exam_passing(request, *args, **kwargs)

    def check_candidate_exam_passing(self, request, *args, **kwargs):
        exam_passing = ExamPassing.objects.get(exam=self.exam, candidate=self.candidate)
        if exam_passing.points < self.exam.passing_grade:
            return HttpResponse(status=403)
        return self.pay_to_candidate(request, *args, **kwargs)

    def pay_to_candidate(self, request, *args, **kwargs):
        oracle_h = OracleHandler()
        txn_hash = oracle_h.pay_to_candidate(self.vacancy.employer.contract_address,
                                             self.candidate.contract_address,
                                             self.vacancy.contract_address)
        save_txn_to_history.delay(self.vacancy.employer.user_id, txn_hash,
                                  'Pay to candidate {} from vacancy {}'.format(self.candidate.contract_address,
                                                                               self.vacancy.contract_address))
        save_txn_to_history.delay(self.candidate.user_id, txn_hash,
                                  'Pay interview fee from vacancy {}'.format(self.vacancy.contract_address))
        can_h = CandidateHandler(settings.WEB_ETH_COINBASE,
                                 self.candidate.contract_address)
        fact = {'from': settings.VERA_ORACLE_CONTRACT_ADDRESS,
                'type': 'vac_pass',
                'title': 'Test for vacancy "{}" passed.'.format(self.vacancy.title),
                'date': time.time(),
                'employer': self.vacancy.employer.organization}
        fact_txn_hash = can_h.new_fact(fact)
        save_txn_to_history.delay(self.candidate.user_id, fact_txn_hash,
                                  'New fact from {}'.format(self.vacancy.employer.organization))
        return super().dispatch(request, *args, **kwargs)

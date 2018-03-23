from django.db import models
from django.db.models import Max
from jsonfield import JSONField


class Category(models.Model):
    title = models.CharField(max_length=255)
    employer = models.ForeignKey('jobboard.Employer',
                                 on_delete=models.CASCADE,
                                 null=True)
    parent_category = models.ForeignKey('self',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True,
                                        related_name='sub_categories')

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('id',)


class QuestionKind(models.Model):
    title = models.CharField(max_length=50)
    template_name = models.CharField(max_length=25,
                                     help_text=u'*_question.html')
    w2v = models.BooleanField(default=False)
    min_answers = models.PositiveSmallIntegerField(default=0)
    one_right_answer = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    question_text = models.TextField(verbose_name=u'Question\'s text')
    weight = models.SmallIntegerField(default=1,
                                      help_text=u'Value from -100 to 100')
    is_published = models.BooleanField(default=True)
    category = models.ForeignKey(Category,
                                 related_name='questions',
                                 on_delete=models.SET_NULL,
                                 null=True)
    kind = models.ForeignKey(QuestionKind,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             default=None,
                             related_name='questions')

    def __str__(self):
        return "{} - {}".format(self.question_text, self.max_points)

    @property
    def max_points(self):
        if self.kind.one_right_answer:
            max_points = self.answers.all().aggregate(Max('weight'))['weight__max'] * self.weight
        else:
            max_points = sum([item.weight for item in self.answers.filter(weight__gt=0)]) * self.weight
        return max_points


class Answer(models.Model):
    text = models.TextField(verbose_name=u'Answer\'s text')
    weight = models.SmallIntegerField(default=1,
                                      help_text=u'Value from -100 to 100')
    question = models.ForeignKey(Question,
                                 related_name='answers',
                                 on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {}'.format(self.text, self.weight)

    class Meta:
        ordering = ('?',)


class VacancyExam(models.Model):
    vacancy = models.ForeignKey('vacancy.Vacancy',
                                on_delete=models.CASCADE,
                                related_name='tests')
    questions = models.ManyToManyField(Question)
    max_attempts = models.PositiveIntegerField(default=3)
    passing_grade = models.PositiveIntegerField(default=0)
    max_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return 'Exam for "{}"'.format(self.vacancy.title)


class ExamPassing(models.Model):
    candidate = models.ForeignKey('jobboard.Candidate',
                                  on_delete=models.SET_NULL,
                                  null=True,
                                  related_name='exams')
    exam = models.ForeignKey(VacancyExam,
                             on_delete=models.SET_NULL,
                             null=True)
    answers = JSONField()
    points = models.IntegerField(default=0)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.candidate, )


class AnswerForVerification(models.Model):
    question = models.ForeignKey(Question,
                                 related_name='verifications',
                                 on_delete=models.CASCADE)
    answer = models.TextField(blank=False,
                              null=False)
    related_answer = models.ForeignKey(Answer,
                                       on_delete=models.SET_NULL,
                                       null=True)
    processed = models.BooleanField(default=False)
    points = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Verification for {}'.format(self.question.question_text)

from django.db import models
from django.db.models import Max, Sum
from django.urls import reverse
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
            max_points = self.answers.all().aggregate(max=Max('weight'))['max'] * self.weight
        else:
            max_points = self.answers.filter(weight__gt=0).aggregate(sum=Sum('weight'))['sum'] * self.weight
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


class ActionExam(models.Model):
    action = models.ForeignKey('pipeline.Action',
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='exam')
    questions = models.ManyToManyField(Question)
    max_attempts = models.PositiveIntegerField(default=3)
    passing_grade = models.PositiveIntegerField(default=0)
    max_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return 'Exam for "{}"'.format(self.action)


class ExamPassed(models.Model):
    cv = models.ForeignKey('cv.CurriculumVitae',
                           on_delete=models.SET_NULL,
                           null=True,
                           related_name='exams')
    exam = models.ForeignKey(ActionExam,
                             on_delete=models.SET_NULL,
                             null=True)
    answers = JSONField()
    points = models.IntegerField(default=0)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.cv.uuid)

    def get_absolute_url(self):
        return reverse('exam_results', kwargs={'pk': self.id})


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

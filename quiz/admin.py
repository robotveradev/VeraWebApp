from django.contrib import admin
from quiz.models import Category, Question, Answer, ActionExam, QuestionKind, ExamPassed, AnswerForVerification


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent_category', 'company']

    class Meta:
        model = Category


class AnswerForVerificationAdmin(admin.ModelAdmin):
    list_display = [i.name for i in AnswerForVerification._meta.fields]

    class Meta:
        model = AnswerForVerification


admin.site.register(Category, CategoryAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(ActionExam)
admin.site.register(QuestionKind)
admin.site.register(ExamPassed)
admin.site.register(AnswerForVerification, AnswerForVerificationAdmin)

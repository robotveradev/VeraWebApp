from django.contrib import admin
from .models import *


class AdminSpecialisation(admin.ModelAdmin):
    list_display = ('title', 'parent')

    class Meta:
        model = Specialisation


class AdminKeywords(admin.ModelAdmin):
    list_display = ('word', )

    class Meta:
        model = Keyword


class AdminCandidate(admin.ModelAdmin):
    list_display = [field.name for field in Candidate._meta.fields]

    class Meta:
        model = Candidate


class AdminCurriculumVitae(admin.ModelAdmin):
    list_display = [field.name for field in CurriculumVitae._meta.fields]

    class Meta:
        model = CurriculumVitae


class AdminEmployer(admin.ModelAdmin):
    list_display = [field.name for field in Employer._meta.fields]

    class Meta:
        model = Employer


class AdminVacancy(admin.ModelAdmin):
    list_display = [field.name for field in Vacancy._meta.fields]

    class Meta:
        model = Vacancy


class AdminTxn(admin.ModelAdmin):
    list_display = [field.name for field in Transactions._meta.fields]

    class Meta:
        model = Transactions


admin.site.register(Specialisation, AdminSpecialisation)
admin.site.register(Keyword, AdminKeywords)
admin.site.register(Candidate, AdminCandidate)
admin.site.register(CurriculumVitae, AdminCurriculumVitae)
admin.site.register(Employer, AdminEmployer)
admin.site.register(Vacancy, AdminVacancy)
admin.site.register(Transactions, AdminTxn)

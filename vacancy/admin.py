from django.contrib import admin

from .models import Vacancy, CandidateOnVacancy


class AdminVacancy(admin.ModelAdmin):
    list_display = ['id', 'company', 'uuid', 'title', 'created_at',
                    'updated_at', 'enabled']

    class Meta:
        model = Vacancy


class CandidateOnVacancyAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CandidateOnVacancy._meta.fields]

    class Meta:
        model = CandidateOnVacancy


admin.site.register(Vacancy, AdminVacancy)
admin.site.register(CandidateOnVacancy, CandidateOnVacancyAdmin)

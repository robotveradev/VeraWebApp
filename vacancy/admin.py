from django.contrib import admin
from .models import Vacancy, CandidateVacancyPassing, VacancyTest


class AdminVacancy(admin.ModelAdmin):
    list_display = ['employer', 'contract_address', 'title', 'city', 'salary_from', 'salary_up_to', 'created_at',
                    'updated_at']

    class Meta:
        model = Vacancy


class AdminTest(admin.ModelAdmin):
    list_display = [field.name for field in VacancyTest._meta.fields]

    class Meta:
        model = VacancyTest


class AdminCandidateVacancyPassing(admin.ModelAdmin):
    list_display = [field.name for field in CandidateVacancyPassing._meta.fields]

    class Meta:
        model = CandidateVacancyPassing


admin.site.register(VacancyTest, AdminTest)
admin.site.register(CandidateVacancyPassing, AdminCandidateVacancyPassing)
admin.site.register(Vacancy, AdminVacancy)

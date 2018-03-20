from django.contrib import admin
from .models import Vacancy


class AdminVacancy(admin.ModelAdmin):
    list_display = ['employer', 'contract_address', 'title', 'city', 'salary_from', 'salary_up_to', 'created_at',
                    'updated_at']

    class Meta:
        model = Vacancy


admin.site.register(Vacancy, AdminVacancy)

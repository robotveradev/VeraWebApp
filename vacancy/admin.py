from django.contrib import admin
from .models import Vacancy


class AdminVacancy(admin.ModelAdmin):
    list_display = ['id', 'employer', 'uuid', 'title', 'city', 'created_at',
                    'updated_at', 'enabled']

    class Meta:
        model = Vacancy


admin.site.register(Vacancy, AdminVacancy)

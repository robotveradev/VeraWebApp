from django.contrib import admin

from .models import Vacancy, MemberOnVacancy


class AdminVacancy(admin.ModelAdmin):
    list_display = ['id', 'company', 'uuid', 'title', 'created_at',
                    'updated_at', 'enabled']

    class Meta:
        model = Vacancy


class MemberOnVacancyAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MemberOnVacancy._meta.fields]

    class Meta:
        model = MemberOnVacancy


admin.site.register(Vacancy, AdminVacancy)
admin.site.register(MemberOnVacancy, MemberOnVacancyAdmin)

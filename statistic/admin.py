from django.contrib import admin
from .models import *


class StatisticAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [i.name for i in self.Meta.model._meta.fields]

    class Meta:
        abstract = True


class CvStatisticAdmin(StatisticAdmin):
    class Meta:
        model = CvStatistic


class VacancyStatisticAdmin(StatisticAdmin):
    class Meta:
        model = VacancyStatistic


admin.site.register(CvStatistic, CvStatisticAdmin)
admin.site.register(VacancyStatistic, VacancyStatisticAdmin)

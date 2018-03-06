from django.contrib import admin
from .models import *


class CurriculumVitaeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CurriculumVitae._meta.fields]

    class Meta:
        model = CurriculumVitae


admin.site.register(CurriculumVitae, CurriculumVitaeAdmin)
admin.site.register(Busyness)
admin.site.register(Schedule)
admin.site.register(Position)
admin.site.register(Experience)
admin.site.register(EducationLevel)
admin.site.register(Education)
admin.site.register(Languages)

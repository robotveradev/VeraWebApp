from django.contrib import admin
from .models import *


class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CandidateProfile._meta.fields]

    class Meta:
        model = CandidateProfile


admin.site.register(CandidateProfile, CandidateProfileAdmin)
admin.site.register(Busyness)
admin.site.register(Schedule)
admin.site.register(Position)
admin.site.register(Experience)
admin.site.register(EducationLevel)
admin.site.register(Education)
admin.site.register(Language)
admin.site.register(LanguageItem)
admin.site.register(Achievement)

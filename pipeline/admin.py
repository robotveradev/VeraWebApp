from django.contrib import admin
from .models import *


class PipelineAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Pipeline._meta.fields]

    class Meta:
        model = Pipeline


class ActionTypeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ActionType._meta.fields]

    class Meta:
        model = ActionType


admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(ActionType, ActionTypeAdmin)

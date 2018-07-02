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


class ActionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Action._meta.fields]
    list_filter = ['pipeline', 'action_type']

    class Meta:
        model = Action


admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(ActionType, ActionTypeAdmin)

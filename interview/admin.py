from django.contrib import admin

from .models import ActionInterview, ScheduledMeeting


class AdminActionInterview(admin.ModelAdmin):
    list_display = ['action', 'start_date', 'end_date']

    class Meta:
        model = ActionInterview


class AdminScheduledMeeting(admin.ModelAdmin):
    list_display = [f.name for f in ScheduledMeeting._meta.fields]

    class Meta:
        model = ScheduledMeeting


admin.site.register(ActionInterview, AdminActionInterview)
admin.site.register(ScheduledMeeting, AdminScheduledMeeting)

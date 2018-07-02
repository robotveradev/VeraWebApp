from rest_framework import serializers

from pipeline.models import Action


class ActionSerializer(serializers.ModelSerializer):
    index = serializers.CharField()
    vacancy = serializers.CharField(source='pipeline.vacancy', read_only=True)
    action_type = serializers.CharField(source='action_type.title', read_only=True)
    exam = serializers.SerializerMethodField()
    interview = serializers.SerializerMethodField()

    def get_exam(self, obj):
        if hasattr(obj, 'exam'):
            return obj.exam.get_absolute_url()

    def get_interview(self, obj):
        if hasattr(obj, 'interview'):
            return obj.interview.get_absolute_url()

    class Meta:
        model = Action
        fields = ('id', 'vacancy', 'action_type', 'index', 'exam', 'interview')

from rest_framework import serializers

from pipeline.models import Pipeline
from pipeline.serializers.ActionSerializer import ActionSerializer


class PipelineSerializer(serializers.ModelSerializer):
    actions = ActionSerializer(many=True)

    class Meta:
        model = Pipeline
        fields = ('id', 'vacancy', 'actions', 'created_at', 'updated_at',)

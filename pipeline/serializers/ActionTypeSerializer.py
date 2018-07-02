from rest_framework import serializers

from pipeline.models import ActionType


class ActionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionType
        fields = ('id', 'title', 'fee')

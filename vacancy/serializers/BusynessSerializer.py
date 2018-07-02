from rest_framework import serializers

from candidateprofile.models import Busyness


class BusynessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Busyness
        fields = ('id', 'title')

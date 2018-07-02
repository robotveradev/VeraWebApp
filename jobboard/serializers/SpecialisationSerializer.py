from rest_framework import serializers

from jobboard.models import Specialisation


class SpecialisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specialisation
        fields = ('id', 'title', 'parent_specialisation')

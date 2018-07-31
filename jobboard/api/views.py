from rest_framework import viewsets

from jobboard.models import Specialisation, Keyword
from jobboard.serializers.EmployerSerializer import EmployerSerializer
from jobboard.serializers.KeywordSerializer import KeywordSerializer
from jobboard.serializers.SpecialisationSerializer import SpecialisationSerializer
from users.models import Member


class SpecialisationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialisation.objects.all()
    serializer_class = SpecialisationSerializer


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer


class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Member.objects.all()
    serializer_class = EmployerSerializer

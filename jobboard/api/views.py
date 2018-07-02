from rest_framework import viewsets, mixins

from jobboard.models import Specialisation, Keyword, Employer
from jobboard.serializers.EmployerFullSerializer import EmployerFullSerializer
from jobboard.serializers.EmployerSerializer import EmployerSerializer
from jobboard.serializers.KeywordSerializer import KeywordSerializer
from jobboard.serializers.SpecialisationSerializer import SpecialisationSerializer


class SpecialisationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialisation.objects.all()
    serializer_class = SpecialisationSerializer


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer


class EmployerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer


class EmployerFullViewSet(viewsets.GenericViewSet,
                          mixins.RetrieveModelMixin):
    queryset = Employer.objects.all()
    serializer_class = EmployerFullSerializer

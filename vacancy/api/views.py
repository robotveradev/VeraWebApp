from rest_framework import viewsets, permissions

from vacancy.models import Vacancy
from jobboard.permissions import IsOwnerOrReadOnly
from vacancy.serializers.VacancySerializer import VacancySerializer


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    serializer_class = VacancySerializer

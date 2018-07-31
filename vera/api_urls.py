from django.urls import path, include
from rest_framework.routers import DefaultRouter

from pipeline.api.views import ActionViewSet, PipelineViewSet, ActionTypesViewSet
from vacancy.api.views import VacancyViewSet
from jobboard.api.views import SpecialisationViewSet, KeywordViewSet, MemberViewSet

router = DefaultRouter()
router.register('vacancies', VacancyViewSet)
router.register('actions', ActionViewSet)
router.register('pipelines', PipelineViewSet)
router.register('jb/keywords', KeywordViewSet)
router.register('jb/specialisation', SpecialisationViewSet)
router.register('jb/actiontypes', ActionTypesViewSet)
router.register('members', MemberViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

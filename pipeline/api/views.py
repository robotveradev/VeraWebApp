from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from jobboard.permissions import IsOwnerOrReadOnly
from pipeline.models import Action, Pipeline, ActionType
from pipeline.serializers.ActionSerializer import ActionSerializer
from pipeline.serializers.ActionTypeSerializer import ActionTypeSerializer
from pipeline.serializers.PipelineSerializer import PipelineSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })


class ActionViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)


class PipelineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provide list and retrive pipeline methods.
    """
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer


class ActionTypesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActionType.objects.all()
    serializer_class = ActionTypeSerializer

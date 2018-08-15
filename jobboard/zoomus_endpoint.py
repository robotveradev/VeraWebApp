from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .tasks import ProcessZoomusEvent


class ZoomusUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.username == 'zoomus_hooker':
            return HttpResponse(status=403)


class ZoomusEndpointView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.process_event(request.body)

    def post(self, request, *args, **kwargs):
        return self.process_event(request.body)

    def process_event(self, data):
        process_event = ProcessZoomusEvent()
        process_event.delay(data)
        return HttpResponse('ok', status=200)

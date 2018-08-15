from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from jobboard.utils import get_w3


class NodeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        w3 = get_w3()
        try:
            sync_now = w3.eth.syncing
        except Exception as e:
            return HttpResponse('Node disabled', status=503)
        else:
            return sync_now and HttpResponse('Node syncing now', status=503)

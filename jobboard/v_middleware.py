from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from web3 import Web3, HTTPProvider


class NodeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        w3 = Web3(HTTPProvider(settings.NODE_URL))
        try:
            w3.eth.syncing
        except Exception as e:
            return HttpResponse('Node disabled', status=503)

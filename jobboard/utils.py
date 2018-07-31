from django.conf import settings
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


def get_w3():
    w3 = Web3(HTTPProvider(settings.NODE_URL))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    return w3

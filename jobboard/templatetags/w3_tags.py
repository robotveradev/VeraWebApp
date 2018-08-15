import time

from django import template
from django.conf import settings
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

register = template.Library()


def get_w3():
    w3 = Web3(HTTPProvider(settings.NODE_URL))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    return w3


@register.filter(name='next_block_in')
def next_block_in(id):
    w3 = get_w3()
    last_block = w3.eth.getBlock('latest')
    return int(time.time() - last_block['timestamp'])


@register.filter(name='time_per_block')
def time_per_block(id):
    w3 = get_w3()
    last_block = w3.eth.getBlock('latest')
    prev_block = w3.eth.getBlock(last_block['number'] - 1)
    return last_block['timestamp'] - prev_block['timestamp']


@register.filter(name='eth_getBalance')
def eth_getBalance(address):
    if address is None:
        return 0
    w3 = get_w3()
    return w3.eth.getBalance(address)

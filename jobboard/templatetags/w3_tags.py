from django import template
from django.conf import settings
from web3 import Web3, HTTPProvider
import datetime
import time

register = template.Library()


@register.filter(name='next_block_in')
def next_block_in(id):
    w3 = Web3(HTTPProvider(settings.NODE_URL))
    last_block = w3.eth.getBlock('latest')
    return int(time.time() - last_block['timestamp'])


@register.filter(next='time_per_block')
def time_per_block(id):
    w3 = Web3(HTTPProvider(settings.NODE_URL))
    last_block = w3.eth.getBlock('latest')
    prev_block = w3.eth.getBlock(last_block['number'] - 1)
    return last_block['timestamp'] - prev_block['timestamp']
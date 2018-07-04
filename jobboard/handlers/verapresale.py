from django.conf import settings
from web3 import Web3, HTTPProvider
import json

from web3.middleware import geth_poa_middleware


class VeraCoinPresaleHandler:
    def __init__(self):
        self.web3 = Web3(HTTPProvider(settings.NODE_URL))
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        with open('jobboard/handlers/verapresale_abi.json', 'r') as abi_definision:
            self.abi = json.load(abi_definision)
        self.contract_address = settings.VERA_COIN_PRESALE_CONTRACT_ADDRESS
        self.password = 'password'
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)

    def fund(self, address, amount):
        txn_hash = self.web3.eth.sendTransaction({'from': address, 'to': self.contract_address, 'value': amount})
        return txn_hash

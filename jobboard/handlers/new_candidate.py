import json

from django.conf import settings
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


class CandidateHandler(object):
    def __init__(self, account, contract_address):
        self.web3 = Web3(HTTPProvider('http://localhost:8545'))
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.account = account
        self.contract_address = contract_address
        self.__password = settings.COINBASE_PASSWORD_SECRET
        with open('jobboard/handlers/new_candidate_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

    def unlockAccount(self):
        self.web3.personal.unlockAccount(self.account, self.__password)

    def get_id(self):
        return self.contract.call().id()

    def pause_cv(self, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).pause_cv(cv_uuid)

    def unpause_cv(self, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).unpause_cv(cv_uuid)

    def subscribe(self, vac_uuid, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).subscribe(vac_uuid, cv_uuid)

    def give_me_a_chance(self, vac_uuid, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).give_me_a_chance(vac_uuid, cv_uuid)

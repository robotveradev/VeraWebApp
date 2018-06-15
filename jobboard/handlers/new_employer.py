from django.conf import settings
from web3 import Web3, HTTPProvider
import json

from web3.middleware import geth_poa_middleware


class EmployerHandler(object):
    def __init__(self, account, contract_address):
        self.web3 = Web3(HTTPProvider('http://localhost:8545'))
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.account = account
        self.contract_address = contract_address
        self.__password = settings.COINBASE_PASSWORD_SECRET
        with open('jobboard/handlers/new_employer_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

    def unlockAccount(self):
        self.web3.personal.unlockAccount(self.account, self.__password)

    def get_id(self):
        return self.contract.call().id()

    def pause_vacancy(self, vac_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).pause_vac(vac_uuid)

    def unpause_vacancy(self, vac_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).unpause_vac(vac_uuid)

    def approve_level_up(self, vac_uuid, can_address):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).approve_level_up(vac_uuid, can_address)

    def approve_money(self, amount):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).approve_money(amount)

    def reset_cv(self, vac_uuid, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).reset_cv(vac_uuid, cv_uuid)

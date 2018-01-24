from web3 import Web3, RPCProvider
import json
import time
from web3.utils.validation import validate_address


class VacancyHandler(object):
    def __init__(self, address, contract_address):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.account = address
        self.contract_address = contract_address
        with open('jobboard/handlers/vacancy_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)
        self.phases = ['not exist', 'wait', 'accepted', 'paid', 'revoked']

    def owner(self):
        return self.contract.call().owner()

    def get_candidate_state(self, address):
        validate_address(address)
        return self.phases[self.contract.call().get_candidate_state(address)]

    def candidates(self):
        return self.contract.call().get_candidates()

    def interview_fee(self):
        return self.contract.call().interview_fee()

    def grant_candidate(self, address):
        validate_address(address)
        if address in self.candidates():
            return self.contract.transact({'from': self.account}).grant_candidate(address)
        return False

    def revoke_candidate(self, address):
        validate_address(address)
        if address in self.candidates():
            return self.contract.transact({'from': self.account}).revoke_candidate(address)
        return False

    def pay_to_candidate(self, address, token):
        if self.get_candidate_state(address) != 'accepted':
            return False
        return self.contract.transact({'from': self.account}).pay_to_candidate(address, token)


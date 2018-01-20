from web3 import Web3, RPCProvider
import json
import time
from web3.utils.validation import validate_address
from web3.utils.events import (
    get_event_data
)


class CandidateHandler(object):
    def __init__(self, address, contract_address):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.account = address
        self.contract_address = contract_address
        with open('jobboard/handlers/candidate_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)
        self.phases = ['not exist', 'wait', 'accepted', 'paid', 'revoked']

    def get_owner(self):
        return self.contract.call().owner()

    def get_id(self):
        return self.contract.call().id()

    def is_allowed(self, address):
        return self.contract.call().allowed_contracts(address)

    def get_facts(self):
        return [Web3.toHex(item) for item in self.contract.call().keys_of_facts()]

    def get_vacancies(self):
        return self.contract.call().get_vacancies()

    def get_vacancy_state(self, address):
        validate_address(address)
        return self.phases[self.contract.call().get_vacancy_state(address)]

    def get_fact(self, id):
        if Web3.toHex(id) in self.get_facts():
            return self.contract.call().get_fact(id)
        else:
            raise TypeError('Invalid FactId')

    def new_fact(self, fact):
        if not isinstance(fact, dict):
            raise TypeError('Fact must be dict')
        return self.contract.transact({'from': self.account}).new_fact(json.dumps(fact))
        # event_abi = self.contract._find_matching_event_abi("NewFact")
        # log_entry = self.web3.eth.getTransactionReceipt(txn_hash)
        # logs = get_event_data(event_abi, log_entry['logs'][0])
        # return logs['args']

    def grant_access_to_contract(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).grant_access(address)

    def revoke_access_to_contract(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).revoke_access(address)

    def subscribe_to_interview(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).subscribe_to_interview(address)

    def unsubscribe_from_interview(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).unsubscribe_from_interview(address)

    def set_vacancy_paid(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).set_vacancy_paid(address)

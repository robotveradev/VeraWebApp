from django.core.serializers.json import DjangoJSONEncoder
from web3 import Web3, RPCProvider
import json
from web3.utils.validation import validate_address
from jobboard.handlers.vacancy import VacancyHandler
from eth_utils import force_bytes, force_text


class CandidateHandler(object):
    def __init__(self, address, contract_address):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.account = address
        self.contract_address = contract_address
        with open('jobboard/handlers/candidate_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)
        self.phases = ['not exist', 'wait', 'accepted', 'paid', 'revoked']

    def owner(self):
        return self.contract.call().owner()

    def get_id(self):
        return self.contract.call().id()

    def is_agent(self, address):
        return self.contract.call().agents(address)

    def paused(self):
        return self.contract.call().paused()

    def get_facts(self):
        fact_keys = []
        for item in self.contract.call().keys_of_facts():
            fact_keys.append(Web3.toHex(force_bytes(item)))
        return fact_keys

    def get_vacancies(self):
        return self.contract.call().get_vacancies()

    def get_vacancy_state(self, address):
        validate_address(address)
        vac_h = VacancyHandler('', address)
        return vac_h.get_candidate_state(self.contract_address)

    def get_fact(self, fact_id):
        if fact_id in self.get_facts():
            return self.contract.call().get_fact(force_text(Web3.toBytes(hexstr=fact_id)))
        else:
            raise TypeError('Invalid FactId')

    def new_fact(self, fact):
        if not isinstance(fact, dict):
            raise TypeError('Fact must be dict')
        return self.contract.transact({'from': self.account}).new_fact(json.dumps(fact, cls=DjangoJSONEncoder))

    def grant_access_to_contract(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).grant_access(address)

    def revoke_access_to_contract(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).revoke_access(address)

    def subscribe_to_interview(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).subscribe_to_interview(address)

    def pause(self):
        return self.contract.transact({'from': self.account}).pause()

    def unpause(self):
        return self.contract.transact({'from': self.account}).unpause()

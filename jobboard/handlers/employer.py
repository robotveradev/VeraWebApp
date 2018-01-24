from web3 import Web3, RPCProvider
import json
import time
from web3.utils.validation import validate_address
from web3.utils.events import (
    get_event_data
)


class EmployerHandler(object):
    def __init__(self, address, contract_address):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.account = address
        self.contract_address = contract_address
        with open('jobboard/handlers/employer_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)
        self.phases = ['not exist', 'enabled', 'disabled']

    def get_id(self):
        return self.contract.call().id()

    def is_allowed(self, address):
        return self.contract.call().allowed_contracts(address)

    def token(self):
        return self.contract.call().token()

    def grant_access_to_contract(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).grant_access(address)

    def revoke_access_to_contract(self, address):
        validate_address(address)
        return self.contract.transact({'from': self.account}).revoke_access(address)

    def grant_access_to_candidate(self, vacancy_address, candidate_address):
        validate_address(vacancy_address)
        validate_address(candidate_address)
        return self.contract.transact({'from': self.account}).grant_access_to_candidate(vacancy_address,
                                                                                        candidate_address)

    def revoke_access_to_candidate(self, vacancy_address, candidate_address):
        validate_address(vacancy_address)
        validate_address(candidate_address)
        return self.contract.transact({'from': self.account}).revoke_access_to_candidate(vacancy_address,
                                                                                         candidate_address)

    def get_vacancies(self):
        return self.contract.call().get_vacancies()

    def new_vacancy(self, allowed_amount, interview_fee):
        return self.contract.transact({'from': self.account}).new_vacancy(allowed_amount, interview_fee)

    def pay_to_candidate(self, vacancy_address, candidate_address):
        validate_address(vacancy_address)
        validate_address(candidate_address)
        return self.contract.transact({'from': self.account}).pay_to_candidate(vacancy_address, candidate_address)

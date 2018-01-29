from web3 import Web3, RPCProvider
import json
from web3.utils.validation import validate_address


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

    def is_agent(self, address):
        return self.contract.call().agents(address)

    def token(self):
        return self.contract.call().token()

    def paused(self):
        return self.contract.call().paused()

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

    def pause(self):
        return self.contract.transact({'from': self.account}).pause()

    def unpause(self):
        return self.contract.transact({'from': self.account}).unpause()

    def pause_vacancy(self, vacancy_address):
        validate_address(vacancy_address)
        return self.contract.transact({'from': self.account}).pause_vacancy(vacancy_address)

    def unpause_vacancy(self, vacancy_address):
        validate_address(vacancy_address)
        return self.contract.transact({'from': self.account}).unpause_vacancy(vacancy_address)

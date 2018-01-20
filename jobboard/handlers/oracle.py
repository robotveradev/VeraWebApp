from web3 import Web3, RPCProvider
import json
from web3.exceptions import BadFunctionCallOutput
from web3.utils.validation import validate_address

from jobboard.handlers.coin import CoinHandler


class OracleHandler(object):
    def __init__(self, account, contract_address):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.account = account
        self.contract_address = contract_address
        with open('jobboard/handlers/oracle_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)
        self.state = ['not exist', 'enabled', 'disabled']

    @property
    def owner(self):
        return self.contract.call().owner()

    @property
    def token(self):
        return self.contract.call().token()

    @property
    def name(self):
        return self.contract.call().name()

    def new_employer(self, e_id, token):
        validate_address(token)
        if self.check_token_is_ERC20(token):
            return self.contract.transact({'from': self.account}).new_employer(e_id, token)
        else:
            return False

    def get_employers(self):
        return self.contract.call().get_employers()

    def get_employer_id(self, address):
        validate_address(address)
        if address in self.get_employers():
            return self.contract.call().get_employer_id(address)
        else:
            raise ValueError("Incorrect Employer")

    def get_employer_state(self, address):
        validate_address(address)
        if address in self.get_employers():
            return self.state[self.contract.call().get_employer_state(address)]
        else:
            raise ValueError("Incorrect Employer")

    def disable_employer(self, address):
        validate_address(address)
        if address in self.get_employers():
            if self.get_employer_state(address) == 'enabled':
                return self.contract.transact({'from': self.account}).disable_employer(address)
            return False
        else:
            raise ValueError("Incorrect Employer")

    def enable_employer(self, address):
        validate_address(address)
        if address in self.get_employers():
            if self.get_employer_state(address) == 'disabled':
                return self.contract.transact({'from': self.account}).enable_employer(address)
            return False
        else:
            raise ValueError("Incorrect Employer")

    def new_candidate(self, c_id):
        return self.contract.transact({'from': self.account}).new_candidate(c_id)
        # event_abi = self.contract._find_matching_event_abi("NewCandidate")
        # log_entry = self.web3.eth.getTransactionReceipt(txn_hash)
        # logs = get_event_data(event_abi, log_entry['logs'][1])
        # return

    def get_candidates(self):
        return self.contract.call().get_candidates()

    def get_candidate_id(self, address):
        validate_address(address)
        if address in self.get_candidates():
            return self.contract.call().get_candidate_id(address)
        else:
            raise ValueError("Incorrect Candidate")

    def get_candidate_state(self, address):
        validate_address(address)
        if address in self.get_candidates():
            return self.state[self.contract.call().get_candidate_state(address)]
        else:
            raise ValueError("Incorrect Candidate")

    def disable_candidate(self, address):
        validate_address(address)
        if address in self.get_candidates():
            if self.get_candidate_state(address) == 'enabled':
                return self.contract.transact({'from': self.account}).disable_candidate(address)
            return False
        else:
            raise ValueError("Incorrect Candidate")

    def enable_candidate(self, address):
        validate_address(address)
        if address in self.get_candidates():
            if self.get_candidate_state(address) == 'disabled':
                return self.contract.transact({'from': self.account}).enable_candidate(address)
            return False
        else:
            raise ValueError("Incorrect candidate")

    def new_vacancy(self, employer_address, allowed_amount, interview_fee):
        validate_address(employer_address)
        if employer_address in self.get_employers():
            return self.contract.transact({'from': self.account}).new_vacancy(employer_address,
                                                                              allowed_amount,
                                                                              interview_fee)
        return False

    def get_vacancies(self):
        return self.contract.call().get_vacancies()

    def get_vacancy_state(self, address):
        validate_address(address)
        if address in self.get_vacancies():
            return self.state[self.contract.call().get_vacancy_state(address)]
        return False

    def disable_vacancy(self, employer_address, vacancy_address):
        validate_address(employer_address)
        validate_address(vacancy_address)
        if employer_address in self.get_employers():
            if vacancy_address in self.get_vacancies():
                return self.contract.transact({'from': self.account}).disable_vacancy(employer_address, vacancy_address)
            else:
                raise ValueError("Incorrect Vacancy")
        else:
            raise ValueError("Incorrect Employer")

    def enable_vacancy(self, employer_address, vacancy_address):
        validate_address(employer_address)
        validate_address(vacancy_address)
        if employer_address in self.get_employers():
            if vacancy_address in self.get_vacancies():
                return self.contract.transact({'from': self.account}).enable_vacancy(employer_address, vacancy_address)
            else:
                raise ValueError("Incorrect Vacancy")
        else:
            raise ValueError("Incorrect Employer")

    def grant_access(self, to_contract, allowance_contract):
        validate_address(to_contract)
        validate_address(allowance_contract)
        return self.contract.transact({'from': self.account}).grant_access(to_contract, allowance_contract)

    def revoke_access(self, to_contract, allowance_contract):
        validate_address(to_contract)
        validate_address(allowance_contract)
        return self.contract.transact({'from': self.account}).revoke_access(to_contract, allowance_contract)

    def check_token_is_ERC20(self, address):
        coin_handler = CoinHandler(address)
        try:
            coin_handler.totalSupply()
            return True
        except ValueError:
            return False
        except BadFunctionCallOutput:
            return False

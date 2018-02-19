from web3 import Web3, RPCProvider
import json
from web3.exceptions import BadFunctionCallOutput
from web3.utils.validation import validate_address
from django.conf import settings
from jobboard.handlers.coin import CoinHandler
from jobboard.handlers.employer import EmployerHandler


class OracleHandler(object):
    def __init__(self, account, contract_address):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.account = account
        self.contract_address = contract_address
        with open('jobboard/handlers/oracle_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.__password = 'onGridTest_lGG%tts%QP'
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)
        self.state = ['not exist', 'enabled', 'disabled']

    def unlockAccount(self):
        self.web3.personal.unlockAccount(self.account, self.__password)

    @property
    def service_fee(self):
        return self.contract.call().service_fee()

    @property
    def vacancy_fee(self):
        return self.contract.call().vacancy_fee()

    @property
    def owner(self):
        return self.contract.call().owner()

    @property
    def name(self):
        return self.contract.call().name()

    def new_employer(self, e_id, token):
        validate_address(token)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_employer(e_id, token)

    def get_employers(self):
        return self.contract.call().get_employers()

    def new_candidate(self, c_id):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_candidate(c_id)

    def get_candidates(self):
        return self.contract.call().get_candidates()

    def new_vacancy(self, address, allowed, fee):
        validate_address(address)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_vacancy(address, allowed, fee)

    def pay_to_candidate(self, emp_address, can_address, vac_address):
        validate_address(emp_address)
        validate_address(can_address)
        validate_address(vac_address)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).pay_to_candidate(emp_address, can_address, vac_address)

    def withdraw(self, from_address, to_address, amount):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).withdraw(settings.VERA_COIN_CONTRACT_ADDRESS,
                                                                       from_address,
                                                                       to_address,
                                                                       amount)

    def pause_contract(self, address):
        validate_address(address)
        self.unlockAccount()
        handler = EmployerHandler(self.account, address)
        return handler.pause()

    def unpause_contract(self, address):
        validate_address(address)
        self.unlockAccount()
        handler = EmployerHandler(self.account, address)
        return handler.unpause()

    def grant_agent(self, address, granted_address):
        validate_address(address)
        self.unlockAccount()
        handler = EmployerHandler(self.account, address)
        return handler.grant_access_to_contract(granted_address)

    def revoke_agent(self, address, revoked_address):
        validate_address(address)
        self.unlockAccount()
        handler = EmployerHandler(self.account, address)
        return handler.revoke_access_to_contract(revoked_address)

    def check_token_is_ERC20(self, address):
        coin_handler = CoinHandler(address)
        try:
            coin_handler.totalSupply()
            return True
        except ValueError:
            return False
        except BadFunctionCallOutput:
            return False

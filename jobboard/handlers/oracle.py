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

    def new_candidate(self, c_id):
        return self.contract.transact({'from': self.account}).new_candidate(c_id)

    def get_candidates(self):
        return self.contract.call().get_candidates()

    def check_token_is_ERC20(self, address):
        coin_handler = CoinHandler(address)
        try:
            coin_handler.totalSupply()
            return True
        except ValueError:
            return False
        except BadFunctionCallOutput:
            return False

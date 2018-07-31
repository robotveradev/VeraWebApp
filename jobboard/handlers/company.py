import json

from django.conf import settings
from solc import compile_files
from web3.utils.validation import validate_address

from jobboard import utils


class CompanyInterface:
    def __init__(self, contract_address, account=None, password=None):
        self.web3 = utils.get_w3()
        self.account = account or settings.WEB_ETH_COINBASE
        self.contract_address = contract_address
        try:
            with open(settings.ABI_PATH + 'Company.abi.json', 'r') as ad:
                self.abi = json.load(ad)
        except FileNotFoundError:
            path = 'dapp/contracts/Company.sol'
            compiled = compile_files([path, ],
                                     output_values=("abi", "ast", "bin", "bin-runtime",))
            with open(settings.ABI_PATH + 'Company.abi.json', 'w+') as ad:
                ad.write(json.dumps(compiled[path + ':Company']['abi']))
                self.abi = compiled[path + ':Company']['abi']
        self.__password = password or settings.COINBASE_PASSWORD_SECRET
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

    def unlockAccount(self):
        return self.web3.personal.unlockAccount(self.account, self.__password)

    def lockAccount(self):
        return self.web3.personal.lockAccount(self.account)

    def new_owner_member(self, address):
        validate_address(address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_owner_member(address)
        self.lockAccount()
        return txn_hash

    def is_owner(self, address):
        return self.contract.call().owners(address)

    def is_collaborator(self, address):
        return self.contract.call().collaborators(address)

    def new_vacancy(self, uuid, allowed):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_vacancy(uuid, allowed)
        self.lockAccount()
        return txn_hash

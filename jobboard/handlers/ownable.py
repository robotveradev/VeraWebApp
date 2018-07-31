import json

from django.conf import settings
from solc import compile_files
from web3.utils.validation import validate_address

from jobboard import utils


class OwnableInterface(object):
    def __init__(self, contract_address, account=None, password=None):
        self.web3 = utils.get_w3()
        self.account = account or settings.WEB_ETH_COINBASE
        self.contract_address = contract_address
        try:
            with open(settings.ABI_PATH + 'Ownable.abi.json', 'r') as ad:
                self.abi = json.load(ad)
        except FileNotFoundError:
            path = 'dapp/contracts/ownership/Ownable.sol'
            compiled = compile_files([path, ],
                                     output_values=("abi", "ast", "bin", "bin-runtime",))
            with open(settings.ABI_PATH + 'Ownable.abi.json', 'w+') as ad:
                ad.write(json.dumps(compiled[path + ':Ownable']['abi']))
                self.abi = compiled[path + ':Ownable']['abi']
        self.__password = password or settings.COINBASE_PASSWORD_SECRET
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

    def unlockAccount(self):
        return self.web3.personal.unlockAccount(self.account, self.__password)

    def lockAccount(self):
        return self.web3.personal.lockAccount(self.account)

    def is_owner(self, address):
        validate_address(address)
        return self.contract.call().owners(address)

    def new_owner(self, address):
        validate_address(address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).newOwner(address)
        self.lockAccount()
        return txn_hash

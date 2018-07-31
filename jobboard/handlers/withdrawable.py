import json

from django.conf import settings
from solc import compile_files
from web3.utils.validation import validate_address

from jobboard import utils


class WithdrawableInterface:
    def __init__(self, contract_address, account=None, password=None):
        self.web3 = utils.get_w3()
        self.account = account or settings.WEB_ETH_COINBASE
        self.contract_address = contract_address
        try:
            with open(settings.ABI_PATH + 'Withdrawable.abi.json', 'r') as ad:
                self.abi = json.load(ad)
        except FileNotFoundError:
            path = 'dapp/contracts/token/Withdrawable.sol'
            compiled = compile_files([path, ],
                                     output_values=("abi", "ast", "bin", "bin-runtime",))
            with open(settings.ABI_PATH + 'Withdrawable.abi.json', 'w+') as ad:
                ad.write(json.dumps(compiled[path + ':Withdrawable']['abi']))
                self.abi = compiled[path + ':Withdrawable']['abi']
        self.__password = password or settings.COINBASE_PASSWORD_SECRET
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)
        self.token_address = settings.VERA_COIN_CONTRACT_ADDRESS

    def unlockAccount(self):
        return self.web3.personal.unlockAccount(self.account, self.__password)

    def lockAccount(self):
        return self.web3.personal.lockAccount(self.account)

    def withdraw(self, address, amount):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).withdraw(self.token_address, address, amount)
        self.lockAccount()
        return txn_hash

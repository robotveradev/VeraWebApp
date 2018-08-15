import json

from django.conf import settings
from solc import compile_files
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


class CandidateHandler(object):
    def __init__(self, contract_address, account=None):
        self.web3 = Web3(HTTPProvider(settings.NODE_URL))
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.account = account or settings.WEB_ETH_COINBASE
        self.contract_address = contract_address
        self.__password = settings.COINBASE_PASSWORD_SECRET
        try:
            with open(settings.ABI_PATH + 'Candidate.abi.json', 'r') as ad:
                self.abi = json.load(ad)
        except FileNotFoundError:
            path = 'dapp/contracts/Candidate.sol'
            compiled = compile_files([path, ],
                                     output_values=("abi", "ast", "bin", "bin-runtime",))
            with open(settings.ABI_PATH + 'Candidate.abi.json', 'w+') as ad:
                ad.write(json.dumps(compiled[path + ':Candidate']['abi']))
                self.abi = compiled[path + ':Candidate']['abi']
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

    def unlockAccount(self):
        self.web3.personal.unlockAccount(self.account, self.__password)

    def lockAccount(self):
        return self.web3.personal.lockAccount(self.account)

    def get_id(self):
        return self.contract.call().id()

    def subscribe(self, vac_uuid):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).subscribe(vac_uuid)
        self.lockAccount()
        return txn_hash

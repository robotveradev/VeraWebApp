import json

from django.conf import settings
from solc import compile_files
from web3.utils.validation import validate_address

from jobboard import utils


class MemberInterface:
    def __init__(self, contract_address):
        self.web3 = utils.get_w3()
        self.account = settings.WEB_ETH_COINBASE
        self.contract_address = contract_address
        try:
            with open(settings.ABI_PATH + 'Member.abi.json', 'r') as ad:
                self.abi = json.load(ad)
        except FileNotFoundError:
            path = 'dapp/contracts/Member.sol'
            compiled = compile_files([path, ],
                                     output_values=("abi", "ast", "bin", "bin-runtime",))
            with open(settings.ABI_PATH + 'Member.abi.json', 'w+') as ad:
                ad.write(json.dumps(compiled[path + ':Member']['abi']))
                self.abi = compiled[path + ':Member']['abi']
        self.__password = settings.COINBASE_PASSWORD_SECRET
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

    def trim0x(self, text):
        return text.rstrip('\x00')

    def unlockAccount(self):
        return self.web3.personal.unlockAccount(self.account, self.__password)

    def lockAccount(self):
        return self.web3.personal.lockAccount(self.account)

    def new_vacancy(self, company_address, uuid, allowed):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_vacancy(company_address, uuid, allowed)
        self.lockAccount()
        return txn_hash

    def new_company_owner(self, company_address, member_address):
        validate_address(company_address)
        validate_address(member_address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_owner_member(company_address, member_address)
        self.lockAccount()
        return txn_hash

    def new_company_collaborator(self, company_address, member_address):
        validate_address(company_address)
        validate_address(member_address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_collaborator_member(company_address,
                                                                                          member_address)
        self.lockAccount()
        return txn_hash

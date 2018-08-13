import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from solc import compile_files
from solc.utils.string import force_bytes
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

    def new_fact(self, member_about_address, fact, fact_uuid):
        validate_address(member_about_address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_fact(member_about_address,
                                                                           json.dumps(fact, cls=DjangoJSONEncoder),
                                                                           fact_uuid)
        self.lockAccount()
        return txn_hash

    def approve_company_tokens(self, company_address, amount):
        validate_address(company_address)
        self.unlockAccount()
        self.contract.transact({'from': self.account}).approve_company_tokens(company_address, 0)
        txn_hash = self.contract.transact({'from': self.account}).approve_company_tokens(company_address, amount)
        self.lockAccount()
        return txn_hash

    def new_vacancy(self, company_address, uuid, allowed):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_vacancy(company_address, uuid, allowed)
        self.lockAccount()
        return txn_hash

    def disable_vac(self, company_address, uuid):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).disable_vac(company_address, uuid)
        self.lockAccount()
        return txn_hash

    def enable_vac(self, company_address, uuid):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).enable_vac(company_address, uuid)
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

    def new_company_member(self, company_address, member_address):
        validate_address(company_address)
        validate_address(member_address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_member(company_address,
                                                                             member_address)
        self.lockAccount()
        return txn_hash

    def new_action(self, company_address, vac_uuid, title, fee, appr):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_vacancy_pipeline_action(company_address,
                                                                                              vac_uuid,
                                                                                              force_bytes(title),
                                                                                              int(float(
                                                                                                  fee)) * 10 ** 18,
                                                                                              appr)
        self.lockAccount()
        return txn_hash

    def del_collaborator_member(self, company_address, member_address):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).del_collaborator_member(company_address,
                                                                                          member_address)
        self.lockAccount()
        return txn_hash

    def del_owner_member(self, company_address, member_address):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).del_owner_member(company_address,
                                                                                   member_address)
        self.lockAccount()
        return txn_hash

    def subscribe(self, company_address, vac_uuid):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).subscribe(company_address,
                                                                            vac_uuid)
        self.lockAccount()
        return txn_hash

    def approve_level_up(self, company_address, vac_uuid, member_address):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).approve_level_up(company_address, vac_uuid,
                                                                                   member_address)
        self.lockAccount()
        return txn_hash

    def reset_candidate_action(self, company_address, vac_uuid, member_address):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).reset_member_action(company_address, vac_uuid,
                                                                                      member_address)
        self.lockAccount()
        return txn_hash

    def change_status(self, status):
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).change_status(status)
        self.lockAccount()
        return txn_hash

    def verify_fact(self, member_address, fact_uuid):
        validate_address(member_address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).verify_fact(member_address, fact_uuid)
        self.lockAccount()
        return txn_hash

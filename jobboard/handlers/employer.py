import json

from django.conf import settings
from solc import compile_files
from solc.utils.string import force_bytes
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


class EmployerHandler(object):
    def __init__(self, contract_address, account=None):
        self.web3 = Web3(HTTPProvider(settings.NODE_URL))
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.account = account or settings.WEB_ETH_COINBASE
        self.contract_address = contract_address
        self.__password = settings.COINBASE_PASSWORD_SECRET
        try:
            with open(settings.ABI_PATH + 'Employer.abi.json', 'r') as ad:
                self.abi = json.load(ad)
        except FileNotFoundError:
            path = 'dapp/contracts/Employer.sol'
            compiled = compile_files([path, ],
                                     output_values=("abi", "ast", "bin", "bin-runtime",))
            with open(settings.ABI_PATH + 'Employer.abi.json', 'w+') as ad:
                ad.write(json.dumps(compiled[path + ':Employer']['abi']))
                self.abi = compiled[path + ':Employer']['abi']
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

    def unlockAccount(self):
        self.web3.personal.unlockAccount(self.account, self.__password)

    def get_id(self):
        return self.contract.call().id()

    def disable_vac(self, vac_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).disable_vac(vac_uuid)

    def enable_vac(self, vac_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).enable_vac(vac_uuid)

    def approve_level_up(self, vac_uuid, can_address):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).approve_level_up(vac_uuid, can_address)

    def reset_candidate_action(self, vac_uuid, can_address):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).reset_candidate_action(vac_uuid, can_address)

    def approve_money(self, amount):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).approve_money(amount)

    def new_action(self, vac_uuid, title, fee, appr):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_vacancy_pipeline_action(vac_uuid,
                                                                                          force_bytes(title),
                                                                                          int(float(fee)) * 10 ** 18,
                                                                                          appr)

    def change_action(self, vac_uuid, index, title, fee, appr):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).change_vacancy_pipeline_action(vac_uuid,
                                                                                             index,
                                                                                             force_bytes(title),
                                                                                             int(float(fee)) * 10 ** 18,
                                                                                             appr)

    def delete_action(self, vac_uuid, index):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).delete_vacancy_pipeline_action(vac_uuid,
                                                                                             index)

    def change_vacancy_allowance_amount(self, vac_uuid, allowed):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).change_vacancy_allowance_amount(vac_uuid, allowed)

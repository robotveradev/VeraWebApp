from web3 import Web3, RPCProvider
import json
from web3.utils.validation import validate_address
from django.conf import settings


class CoinHandler(object):
    def __init__(self, contract_address=None, account=None):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.contract_address = contract_address or settings.VERA_COIN_CONTRACT_ADDRESS
        self.account = account
        with open('jobboard/handlers/coin_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)

    def owner(self):
        return self.contract.call().owner()

    def balanceOf(self, address):
        validate_address(address)
        return self.contract.call().balanceOf(address)

    @property
    def symbol(self):
        return self.contract.call().symbol()

    @property
    def decimals(self):
        return self.contract.call().decimals()

    def totalSupply(self):
        return self.contract.call().totalSupply()

    def allowance(self, owner, spender):
        validate_address(owner)
        validate_address(spender)
        return self.contract.call().allowance(owner, spender)

    def transfer(self, address, amount):
        validate_address(address)
        self.contract.transact({'from': settings.WEB_ETH_COINBASE}).transfer(address, amount)

    # def approve(self, vacancy_address, amount):
    #     if self.account is None:
    #         return False
    #     validate_address(vacancy_address)
    #     return self.contract.transact({'from': self.account}).approve(vacancy_address, amount)

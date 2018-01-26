from web3 import Web3, RPCProvider
import json


class VeraCoinPresaleHandler:
    def __init__(self):
        self.web3 = Web3(RPCProvider(host='localhost', port='8545'))
        with open('jobboard/handlers/verapresale_abi.json', 'r') as abi_definision:
            self.abi = json.load(abi_definision)
        self.contract_address = '0x9AF242B715F818eEb4E485CAe925e1FCF696c696'
        self.password = 'password'
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)

    def fund(self, address, amount):
        txn_hash = self.web3.eth.sendTransaction({'from': address, 'to': self.contract_address, 'value': amount})
        return txn_hash

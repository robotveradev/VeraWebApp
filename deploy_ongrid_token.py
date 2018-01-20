import time
from web3 import Web3
from solc import compile_source

with open('GridCoin.sol', 'r') as file:
    source_code = file.read()

web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

compile_sol = compile_source(source_code)

VeraCoin = web3.eth.contract(
    abi=compile_sol['<stdin>:GridCoin']['abi'],
    bytecode=compile_sol['<stdin>:GridCoin']['bin'],
    bytecode_runtime=compile_sol['<stdin>:GridCoin']['bin-runtime'],
)

coin_trans_hash = VeraCoin.deploy(transaction={'from': web3.eth.accounts[0]})

tx = web3.eth.getTransaction(coin_trans_hash)

while tx is None:
    tx = web3.eth.getTransaction(coin_trans_hash)
    print('.')
    time.sleep(60)

trans_receipt = web3.eth.getTransactionReceipt(coin_trans_hash)

contract_address = trans_receipt['contractAddress']

print(contract_address)

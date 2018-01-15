from web3 import Web3
from solc import compile_source
import re

with(open('VeraCoin.sol', 'r')) as file:
    source_code = file.read()

web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

compile_sol = compile_source(source_code)

VeraCoin = web3.eth.contract(
    abi=compile_sol['<stdin>:VeraCoin']['abi'],
    bytecode=compile_sol['<stdin>:VeraCoin']['bin'],
    bytecode_runtime=compile_sol['<stdin>:VeraCoin']['bin-runtime'],
)

coin_trans_hash = VeraCoin.deploy(transaction={'from': web3.eth.accounts[0]})

trans_receipt = web3.eth.getTransactionReceipt(coin_trans_hash)

contract_address = trans_receipt['contractAddress']

with open('vera/settings.py', 'r') as file_in:
    sett = file_in.read()

text = re.sub("VERA_COIN_CONTRACT_ADDRESS = '\w*'", "VERA_COIN_CONTRACT_ADDRESS = '" + contract_address + "'", sett)

with open("vera/settings.py", "w") as file_out:
    file_out.write(text)

vera_oracle_deploy_args = [contract_address, "VeraOracle"]

VeraOracle = web3.eth.contract(
    abi=compile_sol['<stdin>:VeraOracle']['abi'],
    bytecode=compile_sol['<stdin>:VeraOracle']['bin'],
    bytecode_runtime=compile_sol['<stdin>:VeraOracle']['bin-runtime'],
)

oracle_txn_hash = VeraOracle.deploy(transaction={'from': web3.eth.accounts[0]}, args=vera_oracle_deploy_args)

oracle_trans_receipt = web3.eth.getTransactionReceipt(oracle_txn_hash)

oracle_contract_address = oracle_trans_receipt['contractAddress']

with open('vera/settings.py') as file_in:
    text = file_in.read()

text = re.sub("VERA_ORACLE_CONTRACT_ADDRESS = '\w*'",
              "VERA_ORACLE_CONTRACT_ADDRESS = '" + oracle_contract_address + "'", text)

text = re.sub(r"WEB_ETH_COINBASE = '\w*'", "WEB_ETH_COINBASE = '" + web3.eth.accounts[0] + "'", text)

with open("vera/settings.py", "w") as file_out:
    file_out.write(text)

print('Well done')

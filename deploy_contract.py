import time
from web3 import Web3
from solc import compile_source
import re


with open('VeraCoin.sol', 'r') as file:
    source_code = file.read()

web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

compile_sol = compile_source(source_code)

vera_oracle_deploy_args = ["VeraOracle", 5, "0x36b0db1ceb5a11131e84dded49eac757fd3ae54d", int(25*10**18)]

VeraOracle = web3.eth.contract(
    abi=compile_sol['<stdin>:VeraOracle']['abi'],
    bytecode=compile_sol['<stdin>:VeraOracle']['bin'],
    bytecode_runtime=compile_sol['<stdin>:VeraOracle']['bin-runtime'],
)

web3.personal.unlockAccount(web3.eth.coinbase, "onGridTest_lGG%tts%QP")

oracle_txn_hash = VeraOracle.deploy(transaction={'from': web3.eth.accounts[0]}, args=vera_oracle_deploy_args)

tx = web3.eth.getTransaction(oracle_txn_hash)
while tx['blockNumber'] is None:
    tx = web3.eth.getTransaction(oracle_txn_hash)
    print('.')
    time.sleep(5)

oracle_trans_receipt = web3.eth.getTransactionReceipt(oracle_txn_hash)

oracle_contract_address = oracle_trans_receipt['contractAddress']

print('VeraOracleContractAddress: {}'.format(oracle_contract_address))

with open('vera/settings.py') as file_in:
    text = file_in.read()

text = re.sub("VERA_ORACLE_CONTRACT_ADDRESS = '\w*'",
              "VERA_ORACLE_CONTRACT_ADDRESS = '" + oracle_contract_address + "'", text)

with open("vera/settings.py", "w") as file_out:
    file_out.write(text)

print('Well done')

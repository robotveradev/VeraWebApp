import time
from web3 import Web3
from solc import compile_source
import re

with open('VeraCoin.sol', 'r') as file:
    source_code = file.read()

web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

compile_sol = compile_source(source_code)

VeraCoin = web3.eth.contract(
    abi=compile_sol['<stdin>:VeraCoin']['abi'],
    bytecode=compile_sol['<stdin>:VeraCoin']['bin'],
    bytecode_runtime=compile_sol['<stdin>:VeraCoin']['bin-runtime'],
)
web3.personal.unlockAccount(web3.eth.coinbase, "onGridTest_lGG%tts%QP")

coin_trans_hash = VeraCoin.deploy(transaction={'from': web3.eth.coinbase})

tx = web3.eth.getTransaction(coin_trans_hash)

while tx['blockNumber'] is None:
    tx = web3.eth.getTransaction(coin_trans_hash)
    print('.')
    time.sleep(5)

trans_receipt = web3.eth.getTransactionReceipt(coin_trans_hash)

coin_contract_address = trans_receipt['contractAddress']
print('Coin contract address: {}'.format(coin_contract_address))

VeraCoinPreSale = web3.eth.contract(
    abi=compile_sol['<stdin>:VeraCoinPreSale']['abi'],
    bytecode=compile_sol['<stdin>:VeraCoinPreSale']['bin'],
    bytecode_runtime=compile_sol['<stdin>:VeraCoinPreSale']['bin-runtime'],
)
web3.personal.unlockAccount(web3.eth.coinbase, "onGridTest_lGG%tts%QP")

vera_coin_presale_deploy_args = [500000,
                                 200000,
                                 coin_contract_address,
                                 "0x36b0db1ceb5a11131e84dded49eac757fd3ae54d",
                                 500000,
                                 250,
                                 1519801719,
                                 5000]

presale_coin_trans_hash = VeraCoinPreSale.deploy(transaction={'from': web3.eth.coinbase},
                                                 args=vera_coin_presale_deploy_args)

tx = web3.eth.getTransaction(presale_coin_trans_hash)

while tx['blockNumber'] is None:
    tx = web3.eth.getTransaction(presale_coin_trans_hash)
    print('.')
    time.sleep(5)

trans_receipt = web3.eth.getTransactionReceipt(presale_coin_trans_hash)

presale_contract_address = trans_receipt['contractAddress']
print('PreSale contract address: {}'.format(presale_contract_address))

vera_oracle_deploy_args = ["VeraOracle", 5, "0x36b0db1ceb5a11131e84dded49eac757fd3ae54d", int(25 * 10 ** 18),
                           coin_contract_address]

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

text = re.sub("WEB_ETH_COINBASE = '\w*'",
              "WEB_ETH_COINBASE = '" + web3.eth.coinbase + "'", text)

text = re.sub("VERA_COIN_CONTRACT_ADDRESS = '\w*'",
              "VERA_COIN_CONTRACT_ADDRESS = '" + coin_contract_address + "'", text)

text = re.sub("VERA_COIN_PRESALE_CONTRACT_ADDRESS = '\w*'",
              "VERA_COIN_PRESALE_CONTRACT_ADDRESS = '" + presale_contract_address + "'", text)

text = re.sub("VERA_ORACLE_CONTRACT_ADDRESS = '\w*'",
              "VERA_ORACLE_CONTRACT_ADDRESS = '" + oracle_contract_address + "'", text)

with open("vera/settings.py", "w") as file_out:
    file_out.write(text)

print('Well done')

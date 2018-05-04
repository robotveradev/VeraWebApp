from solc import compile_source
import json

with open('VeraCoin.sol', 'r') as file:
    source_code = file.read()

compile_sol = compile_source(source_code)

with open('jobboard/handlers/oracle_abi.json', 'w') as oracle_abi:
    oracle_abi.write(json.dumps(compile_sol['<stdin>:VeraOracle']['abi']))

with open('jobboard/handlers/employer_abi.json', 'w') as oracle_abi:
    oracle_abi.write(json.dumps(compile_sol['<stdin>:Employer']['abi']))

with open('jobboard/handlers/candidate_abi.json', 'w') as oracle_abi:
    oracle_abi.write(json.dumps(compile_sol['<stdin>:Candidate']['abi']))

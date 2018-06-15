import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from solc import compile_files
from solc.utils.string import force_bytes
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.utils.validation import validate_address


class OracleHandler(object):
    def __init__(self):
        self.web3 = Web3(HTTPProvider('http://localhost:8545'))
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.account = self.web3.eth.coinbase
        self.contract_address = settings.VERA_ORACLE_CONTRACT_ADDRESS
        try:
            with open(settings.ABI_PATH + 'Oracle.abi.json', 'r') as ad:
                self.abi = json.load(ad)
        except FileNotFoundError:
            path = 'dapp/contracts/Oracle.sol'
            compiled = compile_files([path, ],
                                     output_values=("abi", "ast", "bin", "bin-runtime",))
            with open(settings.ABI_PATH + 'Oracle.abi.json', 'w+') as ad:
                ad.write(json.dumps(compiled[path + ':Oracle']['abi']))
                self.abi = compiled[path + ':Oracle']['abi']
        self.__password = settings.COINBASE_PASSWORD_SECRET
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)
        self.state = ['not exist', 'enabled', 'disabled']

    def trim0x(self, text):
        return text.rstrip('\x00')

    def parse_action(self, action):
        return dict(zip(['id', 'title', 'fee', 'approvable'], action))

    def parse_vacancy(self, vac):
        return dict(zip(['uuid', 'approveable', 'allowed_amount'], vac))

    def unlockAccount(self):

        self.web3.personal.unlockAccount(self.account, self.__password)

    @property
    def service_fee(self):
        return self.contract.call().service_fee()

    def new_service_fee(self, new_fee):
        self.unlockAccount()
        self.contract.transact({'from': self.account}).new_service_fee(new_fee)

    @property
    def beneficiary(self):
        return self.contract.call().beneficiary()

    def new_beneficiary(self, new_ben):
        self.unlockAccount()
        self.contract.transact({'from': self.account}).new_beneficiary(new_ben)

    def is_owner(self, address):
        validate_address(address)
        return self.contract.call().owners(address)

    @property
    def name(self):
        return self.contract.call().name()

    @property
    def pipeline_max_length(self):
        return self.contract.call().pipeline_max_length()

    def new_pipeline_max_length(self, new_length):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_pipeline_max_length(new_length)

    def new_employer(self, address):
        validate_address(address)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_employer(address)

    def get_employers(self):
        return self.contract.call().get_employers()

    def new_candidate(self, address):
        validate_address(address)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_candidate(address)

    def get_candidates(self):
        return self.contract.call().get_candidates()

    def new_vacancy(self, employer_address, uuid, allowed):
        validate_address(employer_address)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_vacancy(employer_address,
                                                                          uuid,
                                                                          int(allowed))

    def new_fact(self, candidate_address, fact):
        if not isinstance(fact, dict):
            raise TypeError('Fact must be dict')
        validate_address(candidate_address)
        return self.contract.transact({'from': self.account}).new_fact(candidate_address,
                                                                       json.dumps(fact, cls=DjangoJSONEncoder))

    def facts_length(self, candidate_address):
        validate_address(candidate_address)
        return self.contract.call().keys_of_facts_length()

    def facts_keys(self, candidate_address):
        validate_address(candidate_address)
        fact_keys = []
        for item in self.contract.call().keys_of_facts(candidate_address):
            fact_keys.append(Web3.toHex(force_bytes(item)))
        return fact_keys

    def fact_key_by_index(self, candidate_address, index):
        validate_address(candidate_address)
        assert index < self.facts_length(candidate_address)
        return self.contract.call().fact_key_by_id(candidate_address, index)

    def fact(self, candidate_address, uuid):
        if uuid in self.facts_keys(candidate_address):
            return self.contract.call().get_fact(candidate_address, uuid)
        else:
            raise TypeError('Invalid FactUUID')

    def employer_vacancies_length(self, employer_address):
        validate_address(employer_address)
        return self.contract.call().employer_vacancies_length(employer_address)

    def candidate_vacancies_length(self, candidate_address):
        validate_address(candidate_address)
        return self.contract.call().candidate_vacancies_length(candidate_address)

    def candidate_vacancy_by_index(self, candidate_address, index):
        validate_address(candidate_address)
        assert (index < self.candidate_vacancies_length(candidate_address))
        return self.contract.call().candidate_vacancies(candidate_address, index)

    def vacancy(self, uuid):
        return self.parse_vacancy(self.contract.call().vacancies(uuid))

    def get_vacancy_pipeline_length(self, uuid):
        return self.contract.call().get_vacancy_pipeline_length(uuid)

    def get_action(self, uuid, index):
        return self.parse_action(self.contract.call().vacancy_pipeline(uuid, index))

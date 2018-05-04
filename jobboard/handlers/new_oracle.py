from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from eth_utils import force_text, force_bytes
from web3 import Web3, RPCProvider
import json
from web3.utils.validation import validate_address


class OracleHandler(object):
    def __init__(self):
        self.web3 = Web3(RPCProvider(host='localhost', port=8545))
        self.account = self.web3.eth.coinbase
        self.contract_address = settings.VERA_ORACLE_CONTRACT_ADDRESS
        with open('jobboard/handlers/new_oracle_abi.json', 'r') as ad:
            self.abi = json.load(ad)
        self.__password = 'onGridTest_lGG%tts%QP'
        self.contract = self.web3.eth.contract(self.abi, self.contract_address)
        self.state = ['not exist', 'enabled', 'disabled']

    def trim0x(self, text):
        return text.rstrip('\x00')

    def parse_action(self, action):
        return {'id': action[0],
                'title': self.trim0x(action[1]),
                'fee': int(action[2]) / 10**18,
                'approvable': action[3]}

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

    def new_vacancy(self, employer_address, uuid, allowed, titles, fees, approve):
        assert len(titles) == len(fees) == len(approve)
        validate_address(employer_address)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_vacancy(employer_address,
                                                                          uuid,
                                                                          int(allowed),
                                                                          titles,
                                                                          fees,
                                                                          approve)

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
            return self.contract.call().get_fact(force_text(Web3.toBytes(hexstr=uuid)))
        else:
            raise TypeError('Invalid FactUUID')

    def new_cv(self, candidate_address, uuid):
        validate_address(candidate_address)
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).new_cv(candidate_address, uuid)

    def vacancies_length(self, employer_address):
        validate_address(employer_address)
        return self.contract.call().vacancies_length(employer_address)

    def cvs_length(self, candidate_address):
        validate_address(candidate_address)
        return self.contract.call().cvs_length(candidate_address)

    def vacancies_on_cv_length(self, cv_uuid):
        return self.contract.call().vacancies_on_cv_length(cv_uuid)

    def vacancies_on_cv(self, cv_uuid):
        count = self.vacancies_on_cv_length(cv_uuid)
        vacancies = []
        for i in range(count):
            vacancies.append(self.vacancy_on_cv_by_index(cv_uuid, i))
        return vacancies

    def vacancy_on_cv_by_index(self, cv_uuid, index):
        return self.contract.call().vacancies_on_cv(cv_uuid, index)

    def cvs_on_vacancy_length(self, vac_uuid):
        return self.contract.call().cvs_on_vacancy_length(vac_uuid)

    def cvs_on_vacancy(self, vac_uuid):
        count = self.cvs_on_vacancy_length(vac_uuid)
        cvs = []
        for i in range(count):
            cvs.append(self.cv_on_vacancy_by_index(vac_uuid, i))
        return cvs

    def cv_on_vacancy_by_index(self, vac_uuid, index):
        return self.contract.call().cvs_on_vacancy(vac_uuid, index)

    def employer_vacancies(self, employer_address):
        validate_address(employer_address)
        return self.contract.call().employer_vacancies(employer_address)

    def candidate_cvs(self, candidate_address):
        validate_address(candidate_address)
        return self.contract.call().candidate_cvs(candidate_address)

    def employer_vacancy_by_id(self, employer_address, index):
        validate_address(employer_address)
        return self.contract.call().employer_vacancy_by_id(employer_address, index)

    def candidate_cv_by_id(self, candidate_address, index):
        validate_address(candidate_address)
        return self.contract.call().candidate_cv_by_id(candidate_address, index)

    def get_vacancy_pipeline_length(self, vac_uuid):
        return self.contract.call().get_vacancy_pipeline_length(vac_uuid)

    def level_up(self, vac_uuid, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).level_up(vac_uuid, cv_uuid)

    def get_cv(self, cv_uuid):
        return self.contract.call().cvs(cv_uuid)

    def get_vacancy(self, vac_uuid):
        return self.contract.call().vacancies(vac_uuid)

    def get_vacancy_allowed_rest(self, vac_uuid):
        return self.get_vacancy(vac_uuid)[2]

    def get_vacancy_paused(self, vac_uuid):
        return self.get_vacancy(vac_uuid)[1]

    def get_vacancy_keeper(self, vac_uuid):
        return self.get_vacancy(vac_uuid)[0]

    def get_cv_paused(self, cv_uuid):
        return self.get_cv(cv_uuid)[1]

    def get_cv_keeper(self, cv_uuid):
        return self.get_cv(cv_uuid)[0]

    def pause_vac(self, vac_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).pause_vac(vac_uuid)

    def unpause_vac(self, vac_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).unpause_vac(vac_uuid)

    def pause_cv(self, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).pause_cv(cv_uuid)

    def unpause_cv(self, cv_uuid):
        self.unlockAccount()
        return self.contract.transact({'from': self.account}).unpause_cv(cv_uuid)

    def current_cv_action_on_vacancy(self, vac_uuid, cv_uuid):
        return self.parse_action(self.contract.call().current_action(vac_uuid, cv_uuid))

    def get_action(self, vac_uuid, index):
        if index < self.get_vacancy_pipeline_length(vac_uuid):
            return self.parse_action(self.contract.call().vacancy_pipeline(vac_uuid, index))

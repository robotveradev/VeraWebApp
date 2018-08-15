import json

from django.conf import settings
from solc import compile_files
from solc.utils.string import force_bytes
from web3 import Web3
from web3.utils.validation import validate_address

from jobboard import utils


class Action(object):
    def __init__(self, a_id, title, fee, approvable, candidates=None):
        self.id = a_id
        self.title = title
        self.fee = fee / 10 ** 18
        self.approvable = approvable
        self.candidates = candidates

    def __str__(self):
        return '{} action'.format(self.id)


class OracleHandler(object):
    def __init__(self):
        self.web3 = utils.get_w3()
        self.account = settings.WEB_ETH_COINBASE
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
        self.statuses = ['Open to suggestions', 'Looking for a job', 'Not accepting offers']

    def trim0x(self, text):
        return text.rstrip('\x00')

    def parse_action(self, action, cans):
        return Action(action[0], action[1], action[2], action[3], cans)

    def parse_vacancy(self, vac):
        return dict(zip(['enabled', 'allowed_amount'], vac))

    def unlockAccount(self):
        return self.web3.personal.unlockAccount(self.account, self.__password)

    def lockAccount(self):
        return self.web3.personal.lockAccount(self.account)

    @property
    def service_fee(self):
        return self.contract.call().service_fee()

    def new_service_fee(self, new_fee):
        self.unlockAccount()
        self.contract.transact({'from': self.account}).new_service_fee(new_fee)
        self.lockAccount()

    @property
    def beneficiary(self):
        return self.contract.call().beneficiary()

    def new_beneficiary(self, new_ben):
        self.unlockAccount()
        self.contract.transact({'from': self.account}).new_beneficiary(new_ben)
        self.lockAccount()

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
        txn_hash = self.contract.transact({'from': self.account}).new_pipeline_max_length(new_length)
        self.lockAccount()
        return txn_hash

    def new_employer(self, address):
        validate_address(address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_employer(address)
        self.lockAccount()
        return txn_hash

    def get_employers(self):
        return self.contract.call().get_employers()

    def new_candidate(self, address):
        validate_address(address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).new_candidate(address)
        self.lockAccount()
        return txn_hash

    def get_candidates(self):
        return self.contract.call().get_candidates()

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

    def get_vacancy_candidates_length(self, vac_uuid):
        return self.contract.call().vacancy_candidates_length(vac_uuid)

    # v3
    def member_status(self, contract_address, only_index=False):
        index = self.contract.call().members_statuses(contract_address)
        return index if only_index else self.statuses[index]

    def get_member_companies(self, address):
        return self.contract.call().get_member_companies(address)

    def get_company_members(self, address):
        return self.contract.call().get_company_members(address)

    def get_company_members_length(self, address):
        return self.contract.call().company_members_length(address)

    def get_members_on_vacancy_by_action_count(self, company_address, vac_uuid):
        members_count = self.contract.call().vacancy_members_length(company_address, vac_uuid)
        counts = {}
        for i in range(members_count):
            member_address = self.contract.call().members_on_vacancy(company_address, vac_uuid, i)
            current_action = self.get_member_current_action_index(company_address, vac_uuid, member_address)
            if not self.member_vacancy_passed(company_address, vac_uuid, member_address):
                if current_action not in counts:
                    counts[current_action] = 1
                else:
                    counts[current_action] += 1
        return counts

    def get_member_current_action_index(self, company_address, vac_uuid, member_address):
        return self.contract.call().get_member_current_action_index(company_address, vac_uuid, member_address)

    def member_vacancy_passed(self, company_address, vac_uuid, member_address):
        return self.contract.call().member_vacancy_pass(company_address, vac_uuid, member_address)

    def get_vacancy_pipeline_length(self, company_address, uuid):
        return self.contract.call().get_vacancy_pipeline_length(company_address, uuid)

    def get_action(self, company_address, vac_uuid, index):
        cans = self.get_members_on_action(company_address, vac_uuid, index)
        try:
            chain_action = self.contract.call().vacancy_pipeline(company_address, vac_uuid, index)
        except Exception as e:
            return Action(index, '', 0, False, cans)
        else:
            return self.parse_action(chain_action, cans)

    def get_members_on_action(self, company_address, vac_uuid, action_index):
        members_count = self.contract.call().vacancy_members_length(company_address, vac_uuid)
        members = []
        for i in range(members_count):
            member_address = self.contract.call().members_on_vacancy(company_address, vac_uuid, i)
            if not self.member_vacancy_passed(company_address, vac_uuid, member_address):
                current_index = self.get_member_current_action_index(company_address, vac_uuid, member_address)
                ai, ci = action_index, current_index
                if ci == ai:
                    members.append(member_address)
        return members

    def get_vacancy_members_length(self, company_address, vac_uuid):
        return self.contract.call().vacancy_members_length(company_address, vac_uuid)

    def get_members_on_vacancy(self, company_address, vac_uuid, passed=False, action_index=False):
        members = []
        for i in range(self.get_vacancy_members_length(company_address, vac_uuid)):
            member = {}
            member.update({'contract_address': self.contract.call().members_on_vacancy(company_address, vac_uuid, i)})
            if passed:
                member.update(
                    {'passed': self.member_vacancy_passed(company_address, vac_uuid, member['contract_address'])})
            if action_index:
                member.update(
                    {'action_index': self.get_member_current_action_index(company_address, vac_uuid,
                                                                          member['contract_address'])})
            members.append(member)
        return members

    def vacancy(self, company_address, uuid):
        return self.parse_vacancy(self.contract.call().vacancies(company_address, uuid))

    def level_up(self, company_address, vac_uuid, member_address):
        validate_address(company_address)
        validate_address(member_address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).level_up(company_address, vac_uuid, member_address)
        self.lockAccount()
        return txn_hash

    def member_vacancies_length(self, member_address):
        validate_address(member_address)
        return self.contract.call().member_vacancies_length(member_address)

    def member_vacancy_by_index(self, member_address, index):
        validate_address(member_address)
        return Web3.toHex(self.contract.call().member_vacancies(member_address, index))

    def member_fact_confirmations(self, sender_address, member_address, fact_uuid):
        return self.contract.call().member_fact_confirmations(sender_address, member_address, fact_uuid)

    def member_facts_confirmations_count(self, member_address, fact_uuid):
        return self.contract.call().facts_confirmations_count(member_address, fact_uuid)

    def member_verified(self, member_address):
        validate_address(member_address)
        return self.contract.call().member_verified(member_address)

    def verify_member(self, member_address):
        validate_address(member_address)
        self.unlockAccount()
        txn_hash = self.contract.transact({'from': self.account}).verify_member(member_address)
        self.lockAccount()
        return txn_hash

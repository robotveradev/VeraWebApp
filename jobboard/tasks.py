from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from web3.utils.events import get_event_data

from jobboard.models import Transaction, Employer, Candidate, Vacancy
from web3 import Web3, HTTPProvider
from solc import compile_source


@periodic_task(run_every=crontab(minute='*/1'))
def check_transactions():
    txns_set = Transaction.objects.all()
    if len(txns_set):
        with open("VeraCoin.sol", "r") as contract:
            compiled_contract = compile_source(contract.read())
        w3 = Web3(HTTPProvider(settings.NODE_URL))
        for txn in txns_set:
            txn_info = w3.eth.getTransaction(txn.txn_hash)
            if txn_info is not None:
                if txn.txn_type == 'NewEmployer':
                    try:
                        emp_o = Employer.objects.get(id=txn.obj_id)
                        log_entry = w3.eth.getTransactionReceipt(txn.txn_hash)
                        abi = get_contact_event_abi(compiled_contract, 'VeraOracle', 'NewEmployer')
                        if not abi:
                            print('Incorrect Event abi (VeraOracle, NewEmployer)' + txn.txn_hash + ' ' + txn.txn_type)
                            continue
                        tx_logs = [item for item in log_entry['logs'] if item['transactionHash'] == txn.txn_hash]
                        logs = get_event_data(abi, tx_logs[1])
                        emp_o.contract_address = logs['args']['employer_address']
                        emp_o.save()
                        txn.delete()
                        print("NewEmployerContract: " + emp_o.organization + ' ' + logs['args']['employer_address'])
                    except Employer.DoesNotExist:
                        txn.delete()
                elif txn.txn_type == 'NewCandidate':
                    try:
                        can_o = Candidate.objects.get(id=txn.obj_id)
                        log_entry = w3.eth.getTransactionReceipt(txn.txn_hash)
                        abi = get_contact_event_abi(compiled_contract, 'VeraOracle', 'NewCandidate')
                        if not abi:
                            print('Incorrect Event abi (VeraOracle, NewCandidate)' + txn.txn_hash + ' ' + txn.txn_type)
                            continue
                        tx_logs = [item for item in log_entry['logs'] if item['transactionHash'] == txn.txn_hash]
                        logs = get_event_data(abi, tx_logs[1])
                        can_o.contract_address = logs['args']['candidate_address']
                        can_o.save()
                        txn.delete()
                        print("NewCandidateContract: " + can_o.first_name + ' ' + logs['args']['candidate_address'])
                    except Candidate.DoesNotExist:
                        txn.delete()
                elif txn.txn_type == 'NewVacancy':
                    try:
                        vac_o = Vacancy.objects.get(id=txn.obj_id)
                        log_entry = w3.eth.getTransactionReceipt(txn.txn_hash)
                        abi = get_contact_event_abi(compiled_contract, 'Employer', 'NewVacancy')
                        if not abi:
                            print('Incorrect Event abi (Employer, NewVacancy)' + txn.txn_hash + ' ' + txn.txn_type)
                            continue
                        tx_logs = [item for item in log_entry['logs'] if item['transactionHash'] == txn.txn_hash]
                        logs = get_event_data(abi, tx_logs[1])
                        vac_o.contract_address = logs['args']['vacancy_address']
                        vac_o.save()
                        txn.delete()
                        print("NewVacancyContract: " + vac_o.title + ' ' + logs['args']['vacancy_address'])
                    except Vacancy.DoesNotExist:
                        txn.delete()
                elif txn.txn_type == 'Subscribe':
                    txn.delete()
                elif txn.txn_type == 'EmpAnswer':
                    txn.delete()


def get_contact_event_abi(compiled_contract, contract_name, event_name):
    try:
        for item in compiled_contract['<stdin>:' + contract_name]['abi']:
            if item['type'] == 'event':
                if item['name'] == event_name:
                    return item
    except KeyError:
        return False

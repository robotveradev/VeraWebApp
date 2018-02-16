from __future__ import absolute_import, unicode_literals
from datetime import timedelta

from celery import shared_task
from celery.task import periodic_task
from django.conf import settings
from web3.utils.events import get_event_data

from jobboard.handlers.candidate import CandidateHandler
from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.vacancy import VacancyHandler
from jobboard.models import Transaction, Employer, Candidate, TransactionHistory
from vacancy.models import Vacancy
from web3 import Web3, HTTPProvider
from solc import compile_source


@periodic_task(run_every=timedelta(seconds=15))
def check_transactions():
    txns_set = Transaction.objects.all()
    if len(txns_set):
        with open("VeraCoin.sol", "r") as contract:
            compiled_contract = compile_source(contract.read())
        w3 = Web3(HTTPProvider(settings.NODE_URL))
        for txn in txns_set:
            txn_info = w3.eth.getTransaction(txn.txn_hash)
            if txn_info['blockNumber'] is not None:
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
                        return True
                    except Employer.DoesNotExist:
                        txn.delete()
                        return True
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
                        return True
                    except Candidate.DoesNotExist:
                        txn.delete()
                        return True
                elif txn.txn_type == 'NewVacancy':
                    try:
                        vac_o = Vacancy.objects.get(id=txn.obj_id)
                        log_entry = w3.eth.getTransactionReceipt(txn.txn_hash)
                        abi = get_contact_event_abi(compiled_contract, 'Employer', 'NewVacancy')
                        if not abi:
                            print('Incorrect Event abi (Employer, NewVacancy)' + txn.txn_hash + ' ' + txn.txn_type)
                            continue
                        tx_logs = [item for item in log_entry['logs'] if item['transactionHash'] == txn.txn_hash]
                        logs = get_event_data(abi, tx_logs[2])
                        vac_o.contract_address = logs['args']['vacancy_address']
                        vac_o.save()
                        txn.delete()
                        print("NewVacancyContract: " + vac_o.title + ' ' + logs['args']['vacancy_address'])
                        return True
                    except Vacancy.DoesNotExist:
                        txn.delete()
                        return True
                elif txn.txn_type == 'Subscribe':
                    txn.delete()
                    return True
                elif txn.txn_type == 'EmpAnswer':
                    txn.delete()
                    return True
                elif txn.txn_type == 'Withdraw':
                    txn.delete()
                    return True
                elif txn.txn_type == 'employerChange':
                    try:
                        emp_o = Employer.objects.get(pk=txn.obj_id)
                        emp_h = EmployerHandler(settings.WEB_ETH_COINBASE, emp_o.contract_address)
                        emp_o.enabled = not emp_h.paused()
                        emp_o.save()
                        txn.delete()
                        print(
                            'Employer change contract ({}) paused to: {}'.format(emp_o.contract_address,
                                                                                 not emp_o.enabled))
                        return True
                    except Employer.DoesNotExist:
                        return True
                elif txn.txn_type == 'candidateChange':
                    try:
                        can_o = Candidate.objects.get(pk=txn.obj_id)
                        can_h = CandidateHandler(settings.WEB_ETH_COINBASE, can_o.contract_address)
                        can_o.enabled = not can_h.paused()
                        can_o.save()
                        txn.delete()
                        print('Candidate change contract ({}) paused to: {}'.format(can_o.contract_address,
                                                                                    not can_o.enabled))
                        return True
                    except Candidate.DoesNotExist:
                        return True
                elif txn.txn_type == 'vacancyChange':
                    try:
                        vac_o = Vacancy.objects.get(pk=txn.obj_id)
                        vac_h = VacancyHandler(settings.WEB_ETH_COINBASE, vac_o.contract_address)
                        vac_o.enabled = not vac_h.paused()
                        vac_o.save()
                        txn.delete()
                        print('Employer ({}) change vacancy ({}) paused to: {}'.format(vac_o.employer.contract_address,
                                                                                       vac_o.contract_address,
                                                                                       not vac_o.enabled))
                        return True
                    except Vacancy.DoesNotExist:
                        return True


def get_contact_event_abi(compiled_contract, contract_name, event_name):
    try:
        for item in compiled_contract['<stdin>:' + contract_name]['abi']:
            if item['type'] == 'event':
                if item['name'] == event_name:
                    return item
    except KeyError:
        return False


@shared_task
def save_txn_to_history(user_id, txn_hash, action):
    txn = TransactionHistory()
    txn.user_id = user_id
    txn.hash = txn_hash
    txn.action = action
    txn.save()
    return True


@shared_task
def save_txn(txn_hash, txn_type, user_id, obj_id, vac_id=None):
    txn = Transaction()
    txn.txn_hash = txn_hash
    txn.txn_type = txn_type
    txn.user_id = user_id
    txn.obj_id = obj_id
    txn.vac_id = vac_id
    txn.save()
    print('New transaction')
    return True

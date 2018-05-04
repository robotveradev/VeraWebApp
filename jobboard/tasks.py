from __future__ import absolute_import, unicode_literals
import os
from celery import shared_task
from django.conf import settings
from solc import compile_source
from cv.models import CurriculumVitae
from jobboard.handlers.new_oracle import OracleHandler
from jobboard.models import Transaction, Employer, Candidate, TransactionHistory
from vacancy.models import Vacancy
from web3 import Web3, HTTPProvider
from celery.app.task import Task
from vera.celery import app


DELETE_ONLY_TXN = ['subscribe', 'empanswer', 'withdraw', 'tokenapprove', ]


class CheckTransaction(Task):
    name = 'CheckTransaction'
    soft_time_limit = 10 * 60

    def __init__(self):
        self.txn_set = Transaction.objects.all()
        self.w3 = Web3(HTTPProvider(settings.NODE_URL))
        self.oracle = OracleHandler()

    def run(self, *args, **kwargs):
        if len(self.txn_set):
            self.process_txns()
        return True

    def process_txns(self):
        for txn in self.txn_set:
            txn_info = self.w3.eth.getTransaction(txn.txn_hash)
            if txn_info['blockNumber'] is not None:
                self.handle_txn(txn)

    def check_txn_status(self, txn):
        receipt = self.w3.eth.getTransactionReceipt(txn.txn_hash)
        return receipt['status']

    def handle_txn(self, txn):
        if txn.txn_type.lower() in DELETE_ONLY_TXN:
            self.delete_txn(txn)
            return True
        if hasattr(self, txn.txn_type.lower()):
            method = getattr(self, txn.txn_type.lower())
            method(txn)

    def get_receipt(self, txn_hash):
        return self.w3.eth.getTransactionReceipt(txn_hash)

    def delete_txn(self, txn):
        txn.delete()

    def newemployer(self, txn):
        try:
            emp_o = Employer.objects.get(id=txn.obj_id)
        except Employer.DoesNotExist:
            txn.delete()
        else:
            tnx_receipt = self.get_receipt(txn.txn_hash)
            emp_o.contract_address = tnx_receipt['contractAddress']
            emp_o.save()
            self.delete_txn(txn)
            add_to_oracle_tnx_hash = self.oracle.new_employer(tnx_receipt['contractAddress'])
            save_txn.delay(add_to_oracle_tnx_hash, 'EmployerAdded', emp_o.user.id, emp_o.id)
            print("NewEmployerContract: " + emp_o.organization + ' ' + tnx_receipt['contractAddress'])

    def newcandidate(self, txn):
        try:
            can_o = Candidate.objects.get(id=txn.obj_id)
        except Candidate.DoesNotExist:
            pass
        else:
            tnx_receipt = self.get_receipt(txn.txn_hash)
            can_o.contract_address = tnx_receipt['contractAddress']
            can_o.save()
            self.delete_txn(txn)
            add_to_oracle_tnx_hash = self.oracle.new_candidate(tnx_receipt['contractAddress'])
            save_txn.delay(add_to_oracle_tnx_hash, 'CandidateAdded', can_o.user.id, can_o.id)
            print("NewCandidateContract: " + can_o.first_name + ' ' + tnx_receipt['contractAddress'])

    def newvacancy(self, txn):
        try:
            vac_o = Vacancy.objects.get(id=txn.obj_id)
        except Vacancy.DoesNotExist:
            pass
        else:
            vac_o.published = True
            vac_o.save()
            self.delete_txn(txn)
            print("NewVacancy: " + vac_o.title + ' ' + vac_o.uuid)

    def newcv(self, txn):
        try:
            cv_o = CurriculumVitae.objects.get(id=txn.obj_id)
        except CurriculumVitae.DoesNotExist:
            pass
        else:
            cv_o.published = True
            cv_o.save()
            self.delete_txn(txn)
            print("NewCv: " + cv_o.uuid)

    def vacancychange(self, txn):
        try:
            vac_o = Vacancy.objects.get(pk=txn.obj_id)
        except Vacancy.DoesNotExist:
            pass
        else:
            vac_o.enabled = not self.oracle.get_vacancy_paused(vac_o.uuid)
            vac_o.save()
            txn.delete()
            print('Employer ({}) change vacancy ({}) paused to: {}'.format(vac_o.employer.contract_address,
                                                                           vac_o.uuid,
                                                                           not vac_o.enabled))

    def employeradded(self, txn):
        try:
            emp_o = Employer.objects.get(id=txn.obj_id)
        except Employer.DoesNotExist:
            pass
        else:
            emp_o.enabled = True
            emp_o.save()
        self.delete_txn(txn)

    def candidateadded(self, txn):
        try:
            can_o = Candidate.objects.get(id=txn.obj_id)
        except Candidate.DoesNotExist:
            pass
        else:
            can_o.enabled = True
            can_o.save()
        self.delete_txn(txn)


app.register_task(CheckTransaction())


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


@shared_task
def new_role_instance(instance):
    oracle = OracleHandler()
    with open('jobboard/contracts/' + instance.__class__.__name__ + '.sol', 'r') as file:
        source_code = file.read()
    web3 = Web3(Web3.HTTPProvider(settings.NODE_URL))
    compile_sol = compile_source(source_code)
    obj = web3.eth.contract(
        abi=compile_sol['<stdin>:' + instance.__class__.__name__]['abi'],
        bytecode=compile_sol['<stdin>:' + instance.__class__.__name__]['bin'],
        bytecode_runtime=compile_sol['<stdin>:' + instance.__class__.__name__]['bin-runtime'],
    )
    args = [web3.toHex(os.urandom(15)), ]
    if isinstance(instance, Employer):
        args.append(settings.VERA_COIN_CONTRACT_ADDRESS)
    args.append(settings.VERA_ORACLE_CONTRACT_ADDRESS)

    oracle.unlockAccount()
    txn_hash = obj.deploy(transaction={'from': oracle.account}, args=args)
    if txn_hash:
        save_txn.delay(txn_hash, 'New' + instance.__class__.__name__, instance.user.id, instance.id)

        save_txn_to_history.delay(instance.user.id, txn_hash,
                                  'Creation of a new {} contract'.format(instance.__class__.__name__))
    else:
        instance.delete()

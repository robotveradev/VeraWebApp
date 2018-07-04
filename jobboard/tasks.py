from __future__ import absolute_import, unicode_literals

import json
import logging
import os

from celery import shared_task
from celery.app.task import Task
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from solc import compile_files
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from interview.models import ScheduledMeeting, InterviewPassed
from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Transaction, Employer, Candidate, TransactionHistory
from pipeline.models import Action
from vacancy.models import Vacancy
from vera.celery import app

DELETE_ONLY_TXN = ['subscribe', 'empanswer', 'withdraw', 'tokenapprove', 'actionchanged', 'changestatus']

logger = logging.getLogger(__name__)


class CheckTransaction(Task):
    name = 'CheckTransaction'
    soft_time_limit = 10 * 60

    def __init__(self):
        self.w3 = Web3(HTTPProvider(settings.NODE_URL))
        self.oracle = OracleHandler()
        self.txn_set = None

    def run(self, *args, **kwargs):
        self.txn_set = Transaction.objects.all()
        if len(self.txn_set):
            self.process_txns()
        return True

    def process_txns(self):
        for txn in self.txn_set:
            txn_info = self.w3.eth.getTransaction(txn.txn_hash)
            if txn_info is not None and txn_info['blockNumber'] is not None:
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
        try:
            txn.delete()
        except AssertionError:
            pass

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
            save_txn.delay(add_to_oracle_tnx_hash.hex(), 'EmployerAdded', emp_o.user.id, emp_o.id)
            print("NewEmployerContract: " + emp_o.full_name + ' ' + tnx_receipt['contractAddress'])

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
            save_txn.delay(add_to_oracle_tnx_hash.hex(), 'CandidateAdded', can_o.user.id, can_o.id)
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

    def newaction(self, txn):
        try:
            act_o = Action.objects.get(pk=txn.obj_id)
        except Action.DoesNotExist:
            pass
        else:
            act_o.published = True
            act_o.save()
            self.delete_txn(txn)
            print("New action added: {}".format(act_o.id))

    def vacancychange(self, txn):
        try:
            vac_o = Vacancy.objects.get(pk=txn.obj_id)
        except Vacancy.DoesNotExist:
            pass
        else:
            vac_o.enabled = self.oracle.vacancy(vac_o.uuid)['enabled']
            vac_o.save()
            txn.delete()
            print('Employer ({}) change vacancy ({}) enabled to: {}'.format(vac_o.employer.contract_address,
                                                                            vac_o.uuid,
                                                                            vac_o.enabled))

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

    def actiondeleted(self, txn):
        try:
            act_o = Action.objects.get(pk=txn.obj_id)
        except Action.DoesNotExist:
            pass
        else:
            Action.objects.filter(pipeline=act_o.pipeline, index__gt=act_o.index).update(index=F('index') - 1)
            act_o.delete()
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
def new_role_instance(instance_id, role):
    try:
        role_class = ContentType.objects.get(app_label='jobboard', model=role.lower())
    except ContentType.DoesNotExist:
        pass
    else:
        instance = role_class.model_class().objects.get(pk=instance_id)
        oracle = OracleHandler()
        web3 = Web3(Web3.HTTPProvider(settings.NODE_URL))
        web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        contract_file = 'dapp/contracts/' + role + '.sol'
        compile_sol = compile_files([contract_file, ], output_values=("abi", "ast", "bin", "bin-runtime",))
        create_abi(compile_sol[contract_file + ':' + role]['abi'], role)
        obj = web3.eth.contract(
            abi=compile_sol[contract_file + ':' + role]['abi'],
            bytecode=compile_sol[contract_file + ':' + role]['bin'],
            bytecode_runtime=compile_sol[contract_file + ':' + role]['bin-runtime'],
        )
        args = [web3.toHex(os.urandom(32)), ]
        if isinstance(instance, Employer):
            args.append(settings.VERA_COIN_CONTRACT_ADDRESS)
        args.append(settings.VERA_ORACLE_CONTRACT_ADDRESS)
        logger.info('Try to unlock account: {}.'.format(oracle.unlockAccount()))
        txn_hash = obj.deploy(transaction={'from': oracle.account}, args=args)
        if txn_hash:
            save_txn.delay(txn_hash.hex(), 'New' + role, instance.user.id, instance.id)

            save_txn_to_history.delay(instance.user.id, txn_hash.hex(),
                                      'Creation of a new {} contract'.format(role))
        else:
            instance.delete()


def create_abi(abi, role):
    abi_file = settings.ABI_PATH + role + '.abi.json'
    if not os.path.exists(abi_file):
        with open(abi_file, 'w+') as f:
            f.write(json.dumps(abi))


class ProcessZoomusEvent(Task):
    name = 'ProcessZoomusEvent'
    soft_time_limit = 10 * 60

    def run(self, event_dict, *args, **kwargs):
        try:
            meeting_id = event_dict['payload']['meeting']['id']
            event = event_dict['event']
        except KeyError:
            pass
        else:
            try:
                meet = ScheduledMeeting.objects.get(conf_id=meeting_id)
            except ScheduledMeeting.DoesNotExist:
                pass
            else:
                if hasattr(self, event):
                    method = getattr(self, event)
                    method(event_dict, meet)

    def meeting_ended(self, event, meeting_object):
        passed = InterviewPassed()
        passed.interview = meeting_object.action_interview
        passed.candidate = meeting_object.candidate
        passed.data = event
        passed.save()
        meeting_object.delete()


app.register_task(ProcessZoomusEvent())

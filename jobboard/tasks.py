from __future__ import absolute_import, unicode_literals

import json
import logging
import os

from celery import shared_task
from celery.app.task import Task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from solc import compile_files
from web3 import Web3, HTTPProvider

from company.models import Company
from interview.models import ScheduledMeeting, InterviewPassed
from jobboard.handlers.company import CompanyInterface
from jobboard.handlers.oracle import OracleHandler
from jobboard.handlers.withdrawable import WithdrawableInterface
from jobboard.models import Transaction, TransactionHistory
from pipeline.models import Action
from users.models import Member
from vacancy.models import Vacancy
from vera.celery import app
from . import utils

DELETE_ONLY_TXN = ['subscribe', 'empanswer', 'withdraw', 'tokenapprove', 'actionchanged', 'changestatus',
                   'addcompanymember', 'changecompanymember']

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

    def newmember(self, txn):
        try:
            member = Member.objects.get(id=txn.obj_id)
        except Member.DoesNotExist:
            txn.delete()
        else:
            tnx_receipt = self.get_receipt(txn.txn_hash)
            member.contract_address = tnx_receipt['contractAddress']
            member.save()
            self.delete_txn(txn)
            print("New Member contract: {} {}".format(member.full_name, tnx_receipt['contractAddress']))

    def newcompany(self, txn):
        try:
            company = Company.objects.get(id=txn.obj_id)
        except Company.DoesNotExist:
            logger.warning('Company with id {} not found. Member will not be added as company owner'.format(txn.obj_id))
            txn.delete()
        else:
            tnx_receipt = self.get_receipt(txn.txn_hash)
            company.contract_address = tnx_receipt['contractAddress']
            company.save()
            oi = CompanyInterface(contract_address=tnx_receipt['contractAddress'])
            txn_hash = oi.new_owner_member(company.created_by.contract_address)
            save_txn_to_history.delay(company.created_by.id, txn_hash.hex(),
                                      'Setting your member address as company owner')
            self.delete_txn(txn)
            print("New Company contract: {} {}".format(company.name, tnx_receipt['contractAddress']))

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
            vac_o.enabled = self.oracle.vacancy(vac_o.company.contract_address, vac_o.uuid)['enabled']
            vac_o.save()
            txn.delete()

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
    txn.user = user_id
    txn.hash = txn_hash
    txn.action = action
    txn.save()
    return True


@shared_task
def save_txn(txn_hash, txn_type, user_id, obj_id, vac_id=None):
    txn = Transaction()
    txn.txn_hash = txn_hash
    txn.txn_type = txn_type
    txn.user = user_id
    txn.obj_id = obj_id
    txn.vac_id = vac_id
    txn.save()
    print('New transaction')
    return True


@shared_task
def new_member_instance(user_id):
    try:
        Member.objects.get(pk=user_id)
    except Member.DoesNotExist:
        logger.error('Member with id {} not found, contract will not be deployed.'.format(user_id))
    else:
        oracle = OracleHandler()
        w3 = utils.get_w3()
        contract_file = 'dapp/contracts/Member.sol'
        compile_sol = compile_files([contract_file, ],
                                    output_values=("abi", "ast", "bin", "bin-runtime",))
        create_abi(compile_sol[contract_file + ':Member']['abi'], 'Member')
        obj = w3.eth.contract(
            abi=compile_sol[contract_file + ':Member']['abi'],
            bytecode=compile_sol[contract_file + ':Member']['bin'],
            bytecode_runtime=compile_sol[contract_file + ':Member']['bin-runtime'],
        )
        args = [settings.VERA_ORACLE_CONTRACT_ADDRESS, ]
        logger.info('Try to unlock account: {}.'.format(oracle.unlockAccount()))
        try:
            txn_hash = obj.deploy(transaction={'from': oracle.account}, args=args)
        except Exception as e:
            logger.warning('Error while deploy new member contract. User {}, ex {}'.format(user_id, e))
        else:
            logger.info('Lock account: {}'.format(oracle.lockAccount()))
            save_txn.delay(txn_hash.hex(), 'NewMember', user_id, user_id)
            save_txn_to_history.delay(user_id, txn_hash.hex(),
                                      'Creation of a new Member contract')


def create_abi(abi, contract):
    abi_file = settings.ABI_PATH + contract + '.abi.json'
    if not os.path.exists(abi_file):
        with open(abi_file, 'w+') as f:
            f.write(json.dumps(abi))


@shared_task
def withdraw_tokens(user_id, member_address, to_address, amount):
    wi = WithdrawableInterface(member_address)
    txn_hash = wi.withdraw(to_address, int(float(amount) * 10 ** 18))
    save_txn_to_history.delay(user_id, txn_hash.hex(),
                              'Withdraw {} Vera token from {} to {}'.format(amount,
                                                                            member_address,
                                                                            to_address))
    save_txn.delay(txn_hash.hex(), 'Withdraw', user_id, user_id)


class ProcessZoomusEvent(Task):
    name = 'ProcessZoomusEvent'
    soft_time_limit = 10 * 60

    def run(self, event_dict, *args, **kwargs):
        event_dict = json.loads(event_dict)
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

    def participant_joined(self, event, meeting_object):
        employer = meeting_object.action_interview.employer
        vacancy = meeting_object.action_interview.vacancy
        candidate = meeting_object.candidate
        message = 'Candidate {} for vacancy {} already started an interview. For join interview click link {}'.format(
            candidate.full_name, vacancy.title, meeting_object.link_start
        )
        send_email.delay(message=message, to=employer.user.email)

    def meeting_jbh(self, event, meeting_object):
        employer = meeting_object.action_interview.employer
        vacancy = meeting_object.action_interview.vacancy
        candidate = meeting_object.candidate
        message = 'Employer {} for vacancy {} already started an interview. For join interview click link {}'.format(
            employer.full_name, vacancy.title, meeting_object.link_join
        )
        send_email.delay(message=message, to=candidate.user.email)


app.register_task(ProcessZoomusEvent())


@shared_task
def send_email(**kwargs):
    to_email = kwargs.get('to')
    message = kwargs.get('message')
    if to_email and message:
        send_mail(subject='Vera interview platform',
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[to_email, ],
                  message=message)
    return True


class CheckSoonMeetings(Task):
    name = 'CheckSoonMeetings'

    def run(self, *args, **kwargs):
        pass


app.register_task(CheckSoonMeetings())

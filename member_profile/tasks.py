import logging
import os

from celery import shared_task
from web3 import Web3

from jobboard.handlers.member import MemberInterface
from jobboard.handlers.oracle import OracleHandler
from jobboard.tasks import save_txn, save_txn_to_history
from users.models import Member

logger = logging.getLogger(__name__)


@shared_task
def change_member_status(member_id, status):
    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        logger.warning('Member {} not found. Status will not be changed.')
        return False
    else:
        mi = MemberInterface(contract_address=member.contract_address)
        try:
            txn_hash = mi.change_status(status)
        except Exception as e:
            logger.error('Error while change member {} status: {}'.format(member_id, e))
            return False
        else:
            save_txn.delay(txn_hash.hex(), 'ChangeStatus', member_id, member_id)
            save_txn_to_history.delay(member_id, txn_hash.hex(),
                                      'Status changed to {}'.format(OracleHandler().statuses[int(status)]))
        return True


@shared_task
def new_member_fact(fact, sender_address, about_address):
    try:
        member = Member.objects.get(contract_address=sender_address)
    except Member.DoesNotExist:
        logger.warning('Cant find member with address {}, fact will not be added'.format(sender_address))
        return False
    else:
        mi = MemberInterface(sender_address)
        try:
            txn_hash = mi.new_fact(about_address, fact, Web3.toHex(os.urandom(32)))
        except Exception as e:
            logger.error('Cant add new member fact: about: {}, e: {}'.format(about_address, e))
            return False
        else:
            save_txn.delay(txn_hash.hex(), 'AddNewFact', member.id, member.id)
            save_txn_to_history.delay(member.id, txn_hash.hex(),
                                      'Added new fact about {}'.format(
                                          about_address == sender_address and 'yourself' or about_address))
    return True


@shared_task
def new_fact_confirmation(sender_address, member_address, fact_uuid):
    try:
        sender = Member.objects.get(contract_address=sender_address)
    except Member.DoesNotExist:
        logger.warning('Member with address {} not found, confirmation will not be added'.format(sender_address))
        return False
    else:
        mi = MemberInterface(sender_address)
        try:
            txn_hash = mi.verify_fact(member_address, fact_uuid)
        except Exception as e:
            logger.error("Cannot verify fact, e: {}".format(e))
            return False
        else:
            save_txn.delay(txn_hash.hex(), 'NewFactConfirmation', sender.id, fact_uuid)
            save_txn_to_history.delay(sender.id, txn_hash.hex(),
                                      'Added fact confirmation for fact {}'.format(fact_uuid))
        return True

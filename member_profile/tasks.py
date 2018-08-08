import logging

from celery import shared_task

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

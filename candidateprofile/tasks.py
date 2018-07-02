from celery import shared_task

from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Candidate
from jobboard.tasks import save_txn, save_txn_to_history


@shared_task
def change_candidate_status(candidate_id, status):
    try:
        candidate = Candidate.objects.get(pk=candidate_id)
    except Candidate.DoesNotExist:
        pass
    else:
        oracle = OracleHandler()
        txn_hash = oracle.change_candidate_status(candidate.contract_address, int(status))
        if txn_hash:
            save_txn.delay(txn_hash.hex(), 'ChangeStatus', candidate.user.id, candidate_id)

            save_txn_to_history.delay(candidate.user.id, txn_hash.hex(),
                                      'Status changed to {}'.format(oracle.statuses[int(status)]))
    return True

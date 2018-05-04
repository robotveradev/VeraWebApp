from __future__ import absolute_import, unicode_literals
from celery import shared_task
from jobboard.tasks import save_txn, save_txn_to_history
from jobboard.handlers.new_oracle import OracleHandler
from cv.models import CurriculumVitae


@shared_task
def new_cv(cv_id):
    try:
        cv = CurriculumVitae.objects.get(pk=cv_id)
    except CurriculumVitae.DoesNotExist:
        return True
    else:
        oracle = OracleHandler()
        txn_hash = oracle.new_cv(cv.candidate.contract_address,
                                 cv.uuid)
        if txn_hash:
            save_txn_to_history.apply_async(args=(cv.candidate.user.id,
                                                  txn_hash,
                                                  'Creation of a new cv'), countdown=2)
            save_txn.apply_async(args=(txn_hash, 'NewCv', cv.candidate.user.id, cv.id), countdown=2)

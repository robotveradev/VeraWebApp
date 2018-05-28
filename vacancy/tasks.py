from __future__ import absolute_import, unicode_literals
from celery import shared_task
from jobboard.tasks import save_txn, save_txn_to_history
from jobboard.handlers.new_oracle import OracleHandler
from vacancy.models import Vacancy


@shared_task
def new_vacancy(vacancy_id, pipeline_actions):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
    except Vacancy.DoesNotExist:
        print('Vacancy {} does not exist'.format(vacancy_id))
    else:
        oracle = OracleHandler()
        txn_hash = oracle.new_vacancy(vacancy.company.employer.contract_address,
                                      vacancy.uuid,
                                      int(vacancy.allowed_amount) * 10 ** 18,
                                      pipeline_actions['titles'],
                                      [int(i) * 10 ** 18 for i in pipeline_actions['fees']],
                                      [str2bool(i) for i in pipeline_actions['approve']])
        if txn_hash:
            save_txn_to_history.apply_async(args=(vacancy.employer.user.id, txn_hash,
                                                  'Creation of a new vacancy: {}'.format(vacancy.title)), countdown=2)
            save_txn.apply_async(args=(txn_hash, 'NewVacancy', vacancy.employer.user.id, vacancy.id), countdown=2)


def str2bool(v):
    return v.lower() in ("yes", "true", "y", "1")

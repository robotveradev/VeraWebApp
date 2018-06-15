from __future__ import absolute_import, unicode_literals
from celery import shared_task
from jobboard.tasks import save_txn, save_txn_to_history
from jobboard.handlers.oracle import OracleHandler
from vacancy.models import Vacancy


@shared_task
def new_vacancy(vacancy_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
    except Vacancy.DoesNotExist:
        print('Vacancy {} does not exist'.format(vacancy_id))
    else:
        oracle = OracleHandler()
        txn_hash = oracle.new_vacancy(vacancy.company.employer.contract_address,
                                      vacancy.uuid,
                                      int(vacancy.allowed_amount) * 10 ** 18)
        if txn_hash:
            save_txn_to_history.apply_async(args=(vacancy.employer.user.id, txn_hash.hex(),
                                                  'Creation of a new vacancy: {}'.format(vacancy.title)), countdown=2)
            save_txn.apply_async(args=(txn_hash.hex(), 'NewVacancy', vacancy.employer.user.id, vacancy.id), countdown=2)

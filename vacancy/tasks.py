from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task

from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.member import MemberInterface
from jobboard.handlers.oracle import OracleHandler
from jobboard.tasks import save_txn, save_txn_to_history
from vacancy.models import Vacancy

logger = logging.getLogger(__name__)


@shared_task
def new_vacancy(vacancy_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
    except Vacancy.DoesNotExist:
        logger.warning('Vacancy {} not found and will not be published'.format(vacancy_id))
    else:
        mi = MemberInterface(contract_address=vacancy.created_by.contract_address)
        txn_hash = mi.new_vacancy(vacancy.company.contract_address,
                                  vacancy.uuid,
                                  int(vacancy.allowed_amount) * 10 ** 18)
        if txn_hash:
            save_txn_to_history.apply_async(args=(vacancy.created_by.id, txn_hash.hex(),
                                                  'Creation of a new vacancy: {}'.format(vacancy.title)), countdown=0.2)
            save_txn.apply_async(args=(txn_hash.hex(), 'NewVacancy', vacancy.created_by.id, vacancy.id), countdown=0.2)
    return True


@shared_task
def change_status(vacancy_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
    except Vacancy.DoesNotExist:
        print('Vacancy {} does not exist'.format(vacancy_id))
    else:
        emp_h = EmployerHandler(contract_address=vacancy.employer.contract_address)
        oracle = OracleHandler()
        bch_vacancy = oracle.vacancy(vacancy.uuid)
        if bch_vacancy['enabled']:
            txn_hash = emp_h.disable_vac(vacancy.uuid)
        else:
            txn_hash = emp_h.enable_vac(vacancy.uuid)
        if txn_hash:
            save_txn_to_history.apply_async(args=(vacancy.employer.user.id, txn_hash.hex(),
                                                  'Vacancy status changed: {}'.format(vacancy.title)), countdown=0.5)
            save_txn.apply_async(args=(txn_hash.hex(), 'VacancyChange', vacancy.employer.user.id, vacancy.id),
                                 countdown=0.5)
    return True


@shared_task
def change_vacancy_allowed_amount(vacancy_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
    except Vacancy.DoesNotExist:
        pass
    else:
        emp_h = EmployerHandler(contract_address=vacancy.employer.contract_address)
        oracle = OracleHandler()
        old_vacancy = oracle.vacancy(vacancy.uuid)
        if old_vacancy['allowed_amount'] != int(vacancy.allowed_amount) * 10 ** 18:
            txn_hash = emp_h.change_vacancy_allowance_amount(vacancy.uuid, int(vacancy.allowed_amount) * 10 ** 18)
            if txn_hash:
                save_txn_to_history.apply_async(args=(vacancy.employer.user.id, txn_hash.hex(),
                                                      'Vacancy allowed amount changed: {}'.format(vacancy.title)),
                                                countdown=1)
                save_txn.apply_async(
                    args=(txn_hash.hex(), 'VacancyAllowedChanged', vacancy.employer.user.id, vacancy.id),
                    countdown=1)

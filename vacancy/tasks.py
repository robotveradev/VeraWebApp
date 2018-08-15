from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task

from jobboard.handlers.member import MemberInterface
from jobboard.handlers.oracle import OracleHandler
from jobboard.tasks import save_txn, save_txn_to_history
from users.models import Member
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
        try:
            txn_hash = mi.new_vacancy(vacancy.company.contract_address,
                                      vacancy.uuid,
                                      int(vacancy.allowed_amount) * 10 ** 18)
        except Exception as e:
            logger.error('Error deploy new vacancy: {}, vacancy deleted'.format(e))
            vacancy.delete()
            return False
        else:
            save_txn_to_history.apply_async(args=(vacancy.created_by.id, txn_hash.hex(),
                                                  'Creation of a new vacancy: {}'.format(vacancy.title)), countdown=0.2)
            save_txn.apply_async(args=(txn_hash.hex(), 'NewVacancy', vacancy.created_by.id, vacancy.id), countdown=0.2)
    return True


@shared_task
def change_status(vacancy_id, member_id):
    try:
        sender = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        logger.warning('Member {} not found, vacancy status will not be changed'.format(member_id))
    else:
        try:
            vacancy = Vacancy.objects.get(pk=vacancy_id)
        except Vacancy.DoesNotExist:
            logger.warning('Vacancy {} does not exist'.format(vacancy_id))
        else:
            oracle = OracleHandler()
            allowed_for_vacancies = 0
            company = vacancy.company
            for vacancy_item in company.vacancies.all():
                allowed_for_vacancies += oracle.vacancy(company.contract_address, vacancy_item.uuid)[
                    'allowed_amount']

            mi = MemberInterface(contract_address=sender.contract_address)
            try:
                txn_hash = mi.approve_company_tokens(company.contract_address, allowed_for_vacancies)
            except Exception as e:
                logger.warning('Cannot approve company tokens: {}'.format(e))
            else:
                save_txn_to_history.delay(member_id, txn_hash.hex(),
                                          'Approving {} tokens for platform'.format(allowed_for_vacancies / 10 ** 18))
                bch_vacancy = oracle.vacancy(vacancy.company.contract_address, vacancy.uuid)

                if bch_vacancy['enabled']:
                    method = getattr(mi, 'disable_vac')
                else:
                    method = getattr(mi, 'enable_vac')

                try:
                    txn_hash = method(company.contract_address, vacancy.uuid)
                except Exception as e:
                    logger.warning('Cant change vacancy {} status: {}'.format(vacancy.id, e))
                else:
                    save_txn_to_history.apply_async(args=(member_id, txn_hash.hex(),
                                                          'Vacancy status changed: {}'.format(vacancy.title)),
                                                    countdown=0.1)
                    save_txn.apply_async(args=(txn_hash.hex(), 'VacancyChange', member_id, vacancy.id),
                                         countdown=0.1)
            return True


@shared_task
def change_vacancy_allowed_amount(vacancy_id, sender_id):
    try:
        sender = Member.objects.get(pk=sender_id)
    except Member.DoesNotExist:
        logger.warning('Member {} not found, vacancy allowed amount will not be changed'.format(sender_id))
        return False
    else:
        try:
            vacancy = Vacancy.objects.get(pk=vacancy_id)
        except Vacancy.DoesNotExist:
            logger.warning('Vacancy {} not found, allowed will not be changed'.format(vacancy_id))
            return False
        else:
            mi = MemberInterface(contract_address=sender.contract_address)

            if vacancy.chain['allowed_amount'] != int(vacancy.allowed_amount) * 10 ** 18:
                try:
                    txn_hash = mi.change_vacancy_allowance_amount(vacancy.company.contract_address, vacancy.uuid,
                                                                  int(vacancy.allowed_amount) * 10 ** 18)
                except Exception as e:
                    logger.error('Error changing vacancy allowed amount: {}'.format(e))
                    return False
                else:
                    save_txn_to_history.apply_async(args=(sender_id, txn_hash.hex(),
                                                          'Vacancy allowed amount changed: {}'.format(vacancy.title)),
                                                    countdown=0.1)
                    save_txn.apply_async(
                        args=(txn_hash.hex(), 'VacancyAllowedChanged', sender_id, vacancy.id),
                        countdown=0.1)
                    return True


@shared_task
def new_subscribe(member_id, vacancy_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
    except Vacancy.DoesNotExist:
        logger.warning('Vacancy {} not found, user {} will not be subscribed'.format(vacancy_id, member_id))
        return False
    else:
        try:
            member = Member.objects.get(pk=member_id)
        except Member.DoesNotExist:
            logger.warning('Member {} not found, and will not be subscribed'.format(member_id))
            return False
        else:
            mi = MemberInterface(contract_address=member.contract_address)
            try:
                txn_hash = mi.subscribe(vacancy.company.contract_address, vacancy.uuid)
            except Exception as e:
                logger.error('Error while subscribe: member {}, vacancy {}, e: {}'.format(member_id, vacancy_id, e))
            else:
                save_txn_to_history.apply_async(args=(member_id, txn_hash.hex(),
                                                      'Subscribe to vacancy: {}'.format(vacancy.title)),
                                                countdown=0.1)
                save_txn.apply_async(
                    args=(txn_hash.hex(), 'MemberSubscribe', member_id, vacancy.id),
                    countdown=0.1)
                return True

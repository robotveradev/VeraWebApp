import logging

from celery import shared_task

from jobboard.handlers.member import MemberInterface
from jobboard.handlers.oracle import OracleHandler
from jobboard.tasks import save_txn_to_history, save_txn
from users.models import Member
from vacancy.models import Vacancy

logger = logging.getLogger(__name__)


@shared_task
def new_action(action):
    mi = MemberInterface(contract_address=action['member_address'])
    try:
        txn_hash = mi.new_action(company_address=action['company_address'],
                                 vac_uuid=action['vacancy_uuid'],
                                 title=action['title'],
                                 fee=action['fee'],
                                 appr=action['approvable'])
    except Exception as e:
        logger.warning('Cant create new action, {} {}'.format(action['id'], e))
        return False
    else:
        vacancy = Vacancy.objects.get(uuid=action['vacancy_uuid'])
        save_txn_to_history.apply_async(args=(action['created_by'], txn_hash.hex(),
                                              'Creation of a new action for vacancy: {}'.format(vacancy.title)),
                                        countdown=0.1)
        save_txn.apply_async(args=(txn_hash.hex(), 'NewAction', action['created_by'], action['id'], vacancy.id),
                             countdown=0.1)
        return True


@shared_task
def changed_action(action):
    try:
        sender = Member.objects.get(pk=action['sender_id'])
    except Member.DoesNotExist:
        logger.warning('Sender {} not found, action will not be changed'.format(action['sender_id']))
        return False
    else:
        try:
            vacancy = Vacancy.objects.get(pk=action['vacancy_id'])
        except Vacancy.DoesNotExist:
            logger.warning('Vacancy {} not found, action will not be changed'.format(action['vacancy_id']))
            return False
        else:
            mi = MemberInterface(contract_address=sender.contract_address)
            try:
                txn_hash = mi.change_action(company_address=vacancy.company.contract_address,
                                            vac_uuid=vacancy.uuid,
                                            index=action['index'],
                                            title=action['title'],
                                            fee=action['fee'],
                                            appr=action['approvable'])
            except Exception as e:
                logger.error('Error while change pipline action {}: {}'.format(action['index'], e))
                return False
            else:
                save_txn_to_history.apply_async(args=(action['sender_id'], txn_hash.hex(),
                                                      'Changed action {} on vacancy: {}'.format(action['index'],
                                                                                                vacancy.title)),
                                                countdown=0.1)
                save_txn.apply_async(args=(txn_hash.hex(), 'ActionChanged', action['sender_id'], action['id']),
                                     countdown=0.1)
                return True


@shared_task
def delete_action(action):
    try:
        sender = Member.objects.get(pk=action['sender_id'])
    except Member.DoesNotExist:
        logger.warning('Sender {} not found. Action will not be deleted'.format(action['sender_id']))
        return False
    else:
        try:
            vacancy = Vacancy.objects.get(id=action['vacancy_id'])
        except Vacancy.DoesNotExist:
            logger.warning('Action vacancy {} not found, action will not be deleted'.format(action['vacancy_id']))
            return False
        else:
            mi = MemberInterface(contract_address=sender.contract_address)
            try:
                txn_hash = mi.delete_action(vacancy.company.contract_address, vacancy.uuid, action['index'])
            except Exception as e:
                logger.error('Error while deleting action {}: {}'.format(action['id'], e))
                return False
            else:
                save_txn_to_history.apply_async(args=(action['sender_id'], txn_hash.hex(),
                                                      'Deleted action {} on vacancy: {}'.format(action['index'],
                                                                                                vacancy.title)),
                                                countdown=0.1)
                save_txn.apply_async(
                    args=(txn_hash.hex(), 'ActionDeleted', action['sender_id'], action['id'], vacancy.id),
                    countdown=0.1)
                return True


@shared_task
def action_with_candidate(vacancy_id, candidate_id, action, sender_id):
    try:
        sender = Member.objects.get(pk=sender_id)
    except Member.DoesNotExist:
        logger.warning('Sender {} not found, candidate {} will not '
                       'be level up or reset on vacancy {}'.format(sender_id,
                                                                   candidate_id,
                                                                   vacancy_id))
        return False
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
    except Vacancy.DoesNotExist:
        logger.warning(
            'Vacancy {} not found, action with candidate {} will not be provided'.format(vacancy_id, candidate_id))
        return False
    else:
        try:
            candidate = Member.objects.get(pk=candidate_id)
        except Member.DoesNotExist:
            logger.warning('Candidate {} do not found, action with vacancy {} will not be provided'.format(candidate_id,
                                                                                                           vacancy_id))
            return False
        else:
            mi = MemberInterface(contract_address=sender.contract_address)
            if action == 'approve':
                method = getattr(mi, 'approve_level_up')
            else:
                method = getattr(mi, 'reset_candidate_action')
            try:
                txn_hash = method(vacancy.company.contract_address, vacancy.uuid, candidate.contract_address)
            except Exception as e:
                logger.error('Error {} member on vacancy {}: {}'.format(action, vacancy_id, e))
            else:
                save_txn.delay(txn_hash.hex(), 'CandidateActionUpDown', sender_id, candidate_id, vacancy_id)
                save_txn_to_history.delay(sender_id, txn_hash.hex(),
                                          'Member {} {} on vacancy {}.'.format(
                                              candidate.full_name,
                                              action == 'approve' and 'approved' or 'revoked',
                                              vacancy.title))
                save_txn_to_history.delay(candidate_id, txn_hash.hex(),
                                          '{} on vacancy {}.'.format(action.capitalize(), vacancy.title))
                return True


@shared_task
def candidate_level_up(vacancy_id, candidate_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
        candidate = Member.objects.get(pk=candidate_id)
    except Vacancy.DoesNotExist:
        logger.warning('Vacancy {} not found, candidate will not be leveled up.'.format(vacancy_id))
        return False
    except Member.DoesNotExist:
        logger.warning('Member {} not found and will not be leveled up.'.format(candidate_id))
        return False
    else:
        oracle = OracleHandler()
        try:
            txn_hash = oracle.level_up(vacancy.company.contract_address, vacancy.uuid, candidate.contract_address)
        except Exception as e:
            logger.error('Error auto level up member {} on vacancy {}: {}'.format(candidate_id, vacancy_id, e))
            return False
        else:
            save_txn_to_history.delay(candidate_id, txn_hash.hex(), 'Level up on vacancy {}'.format(vacancy.title))
        return True

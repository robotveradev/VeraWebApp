import logging

from celery import shared_task

from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.member import MemberInterface
from jobboard.handlers.oracle import OracleHandler
from jobboard.tasks import save_txn_to_history, save_txn
from users.models import Member
from vacancy.models import Vacancy, MemberOnVacancy

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
    else:
        vacancy = Vacancy.objects.get(uuid=action['vacancy_uuid'])
        save_txn_to_history.apply_async(args=(action['created_by'], txn_hash.hex(),
                                              'Creation of a new action for vacancy: {}'.format(vacancy.title)),
                                        countdown=0.1)
        save_txn.apply_async(args=(txn_hash.hex(), 'NewAction', action['created_by'], action['id'], vacancy.id),
                             countdown=0.1)


@shared_task
def changed_action(action):
    emp_h = EmployerHandler(contract_address=action['contract_address'])
    txn_hash = emp_h.change_action(vac_uuid=action['vacancy_uuid'],
                                   index=action['index'],
                                   title=action['title'],
                                   fee=action['fee'],
                                   appr=action['approvable'])
    if txn_hash:
        vacancy = Vacancy.objects.get(uuid=action['vacancy_uuid'])
        save_txn_to_history.apply_async(args=(vacancy.employer.user.id, txn_hash.hex(),
                                              'Changed action {} on vacancy: {}'.format(action['index'],
                                                                                        vacancy.title)),
                                        countdown=0.1)
        save_txn.apply_async(args=(txn_hash.hex(), 'ActionChanged', vacancy.employer.user.id, action['id']),
                             countdown=0.1)


@shared_task
def delete_action(action):
    vacancy = Vacancy.objects.get(id=action['vacancy_id'])
    emp_h = EmployerHandler(contract_address=vacancy.employer.contract_address)
    txn_hash = emp_h.delete_action(vacancy.uuid, action['index'])
    if txn_hash:
        save_txn_to_history.apply_async(args=(vacancy.employer.user.id, txn_hash.hex(),
                                              'Deleted action {} on vacancy: {}'.format(action['index'],
                                                                                        vacancy.title)),
                                        countdown=0.1)
        save_txn.apply_async(args=(txn_hash.hex(), 'ActionDeleted', vacancy.employer.user.id, action['id'], vacancy.id),
                             countdown=0.1)


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
    else:
        try:
            candidate = Member.objects.get(pk=candidate_id)
        except Member.DoesNotExist:
            logger.warning('Candidate {} do not found, action with vacancy {} will not be provided'.format(candidate_id,
                                                                                                           vacancy_id))
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


@shared_task
def candidate_level_up(vacancy_id, candidate_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
        candidate = Member.objects.get(pk=candidate_id)
    except Vacancy.DoesNotExist:
        logger.warning('Vacancy {} not found, candidate will not be leveled up.'.format(vacancy_id))
    except Member.DoesNotExist:
        logger.warning('Member {} not found and will not be leveled up.'.format(candidate_id))
    else:
        oracle = OracleHandler()
        try:
            txn_hash = oracle.level_up(vacancy.company.contract_address, vacancy.uuid, candidate.contract_address)
        except Exception as e:
            logger.error('Error auto level up member {} on vacancy {}: {}'.format(candidate_id, vacancy_id, e))
        else:
            save_txn_to_history.delay(candidate_id, txn_hash.hex(), 'Level up on vacancy {}'.format(vacancy.title))
    return True

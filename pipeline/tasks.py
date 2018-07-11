from celery import shared_task

from jobboard.handlers.employer import EmployerHandler
from jobboard.models import Candidate
from jobboard.tasks import save_txn_to_history, save_txn
from vacancy.models import Vacancy, CandidateOnVacancy


@shared_task
def new_action(action):
    emp_h = EmployerHandler(contract_address=action['contract_address'])
    txn_hash = emp_h.new_action(vac_uuid=action['vacancy_uuid'],
                                title=action['title'],
                                fee=action['fee'],
                                appr=action['approvable'])
    if txn_hash:
        vacancy = Vacancy.objects.get(uuid=action['vacancy_uuid'])
        save_txn_to_history.apply_async(args=(vacancy.employer.user.id, txn_hash.hex(),
                                              'Creation of a new action for vacancy: {}'.format(vacancy.title)),
                                        countdown=0.1)
        save_txn.apply_async(args=(txn_hash.hex(), 'NewAction', vacancy.employer.user.id, action['id'], vacancy.id),
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
def action_with_candidate(vacancy_id, candidate_id, action):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
        candidate = Candidate.objects.get(pk=candidate_id)
    except Vacancy.DoesNotExist:
        pass
    except Candidate.DoesNotExist:
        pass
    else:
        emp_h = EmployerHandler(contract_address=vacancy.employer.contract_address)
        if action == 'approve':
            txn_hash = emp_h.approve_level_up(vacancy.uuid, candidate.contract_address)
        else:
            txn_hash = emp_h.reset_candidate_action(vacancy.uuid, candidate.contract_address)
            CandidateOnVacancy.objects.filter(vacancy=vacancy, candidate=candidate).delete()

        save_txn_to_history.delay(vacancy.owner.id, txn_hash.hex(),
                                  'Candidate {} {} on vacancy {}.'.format(
                                      candidate.full_name,
                                      action == 'approve' and 'approved' or 'revoked',
                                      vacancy.title))
        save_txn_to_history.delay(candidate.user.id, txn_hash.hex(),
                                  '{} on vacancy {}.'.format(action.capitalize(), vacancy.title))


@shared_task
def candidate_level_up(vacancy_id, candidate_id):
    try:
        vacancy = Vacancy.objects.get(pk=vacancy_id)
        candidate = Candidate.objects.get(pk=candidate_id)
    except Vacancy.DoesNotExist:
        pass
    except Candidate.DoesNotExist:
        pass
    else:
        emp_h = EmployerHandler(contract_address=vacancy.employer.contract_address)
        txn_hash = emp_h.approve_level_up(vacancy.uuid, candidate.contract_address)
        save_txn_to_history.delay(candidate.user.id, txn_hash.hex(), 'Level up on vacancy {}'.format(vacancy.title))
    return True

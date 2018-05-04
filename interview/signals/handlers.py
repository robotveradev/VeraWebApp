from django.db.models.signals import post_save
from django.dispatch import receiver
from jobboard.handlers.new_employer import EmployerHandler
from jobboard.tasks import save_txn_to_history
from interview.models import Interview
from django.conf import settings


@receiver(post_save, sender=Interview)
def candidate_pass_interview(sender, instance, created, **kwargs):
    if hasattr(instance, 'type'):
        vacancy = instance.action_interview.action.pipeline.vacancy
        employer = EmployerHandler(settings.WEB_ETH_COINBASE, vacancy.employer.contract_address)
        if instance.type == 'approve':
            txn_hash = employer.approve_level_up(vacancy.uuid, instance.cv.uuid)
        elif instance.type == 'revoke':
            txn_hash = employer.revoke_cv(vacancy.uuid, instance.cv.uuid)
        save_txn_to_history.delay(instance.cv.candidate.user.id, txn_hash,
                                  '{}d on vacancy {}'.format(instance.type.capitalize(),
                                                             instance.action_interview.action.pipeline.vacancy.title))
        save_txn_to_history.delay(vacancy.employer.user.id, txn_hash,
                                  'CV {} {}d on vacancy {}'.format(instance.cv.uuid, instance.type,
                                                                   instance.action_interview.action.pipeline.vacancy.title))

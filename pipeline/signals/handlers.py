from django.db.models.signals import post_save
from django.dispatch import receiver

from pipeline.models import Action
from pipeline.tasks import new_action, changed_action, delete_action


@receiver(post_save, sender=Action)
def action_handler(sender, instance, created, **kwargs):
    if hasattr(instance, 'fee') and hasattr(instance, 'approvable'):
        if not created:
            action = {
                'id': instance.id,
                'title': instance.action_type.title,
                'fee': instance.fee,
                'approvable': instance.approvable,
                'vacancy_uuid': instance.pipeline.vacancy.uuid,
                'contract_address': instance.pipeline.owner.contract_address,
                'index': instance.index
            }
            changed_action.delay(action)
        elif created:
            if instance.fee == '':
                instance.fee = 0
            action = {
                'id': instance.id,
                'title': instance.action_type.title,
                'fee': instance.fee,
                'approvable': instance.approvable,
                'vacancy_uuid': instance.pipeline.vacancy.uuid,
                'contract_address': instance.pipeline.owner.contract_address
            }
            new_action.delay(action)
    elif instance.to_delete:
        correction = Action.objects.filter(pipeline=instance.pipeline, to_delete=True,
                                           index__lt=instance.index).count()
        action = {
            'index': instance.index - correction,
            'id': instance.id,
            'vacancy_id': instance.pipeline.vacancy.id
        }
        delete_action.delay(action)

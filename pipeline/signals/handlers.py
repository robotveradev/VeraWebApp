from django.db.models import F
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver

from pipeline.models import Action
from pipeline.tasks import new_action, changed_action, delete_action


@receiver(post_save, sender=Action)
def create_action(sender, instance, created, **kwargs):
    if created and hasattr(instance, 'fee') and hasattr(instance, 'approvable'):
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


@receiver(post_save, sender=Action)
def change_action_handler(sender, instance, created, **kwargs):
    if not created and hasattr(instance, 'fee') and hasattr(instance, 'approvable'):
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
    elif hasattr(instance, 'to_delete'):
        print('БУДУ УДАЛЯТЬ')
        action = {
            'index': instance.index,
            'id': instance.id,
            'vacancy_id': instance.pipeline.vacancy.id
        }
        delete_action.delay(action)

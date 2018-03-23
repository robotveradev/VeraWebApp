from django.db.models.signals import post_save
from django.dispatch import receiver

from jobboard.handlers.employer import EmployerHandler
from jobboard.handlers.oracle import OracleHandler
from jobboard.handlers.vacancy import VacancyHandler
from vacancy.models import Vacancy
from jobboard.tasks import save_txn_to_history, save_txn


@receiver(post_save, sender=Vacancy)
def new_vacancy(sender, instance, created, **kwargs):
    if created:
        oracle = OracleHandler()
        txn_hash = oracle.new_vacancy(instance.employer.contract_address,
                                      int(instance.allowed_amount) * 10 ** 18,
                                      int(instance.interview_fee) * 10 ** 18)
        if txn_hash:
            save_txn_to_history.apply_async(args=(instance.employer.user.id, txn_hash,
                                                  'Creation of a new vacancy: {}'.format(instance.title)), countdown=5)
            save_txn.apply_async(args=(txn_hash, 'NewVacancy', instance.employer.user.id, instance.id), countdown=5)
        else:
            instance.delete()
    else:
        if instance.enabled is None and instance.contract_address is not None:
            print('Начинаю!')
            oracle = OracleHandler()
            oracle.unlockAccount()
            vacancy_handler = VacancyHandler(oracle.account, instance.contract_address)
            employer_handler = EmployerHandler(oracle.account, instance.employer.contract_address)
            if vacancy_handler.paused() is True:
                txn_hash = employer_handler.unpause_vacancy(instance.contract_address)
            else:
                txn_hash = employer_handler.pause_vacancy(instance.contract_address)

                save_txn.delay(txn_hash, 'vacancyChange', instance.employer.user.id, instance.id)
                save_txn_to_history.delay(instance.employer.user.id, txn_hash,
                                          'Change vacancy {} status'.format(instance.contract_address))

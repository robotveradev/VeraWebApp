from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver

from jobboard.handlers.new_oracle import OracleHandler
from jobboard.tasks import save_txn_to_history
from quiz.models import ExamPassed, AnswerForVerification, ActionExam
from quiz.tasks import ProcessExam, VerifyAnswer


@receiver(post_save, sender=ExamPassed)
def candidate_pass_exam(sender, instance, created, **kwargs):
    if created:
        pr = ProcessExam()
        pr.delay(instance.id)
    else:
        if instance.processed and instance.points >= instance.exam.passing_grade:
            oracle = OracleHandler()
            print(oracle.current_cv_action_on_vacancy(instance.exam.action.pipeline.vacancy.uuid, instance.cv.uuid))
            txn_hash = oracle.level_up(instance.exam.action.pipeline.vacancy.uuid, instance.cv.uuid)
            save_txn_to_history.delay(instance.cv.candidate.user.id, txn_hash,
                                      'Level up on vacancy {}'.format(instance.exam.action.pipeline.vacancy.title))


@receiver(pre_save, sender=AnswerForVerification)
def clear_older_answers(sender, instance, **kwargs):
    if instance.id is None:
        AnswerForVerification.objects.filter(question=instance.question).delete()


@receiver(post_save, sender=AnswerForVerification)
def process_verification(sender, instance, created, **kwargs):
    if created:
        va = VerifyAnswer()
        va.delay(instance.id)


@receiver(m2m_changed, sender=ActionExam.questions.through)
def recount_points(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', ]:
        max_points = sum([item.max_points for item in instance.questions.all()])
        if instance.passing_grade == 0:
            instance.passing_grade = max_points
        else:
            instance.passing_grade = max_points * (instance.passing_grade / instance.max_points)
        instance.max_points = max_points
        instance.save()

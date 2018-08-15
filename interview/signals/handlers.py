from django.db.models.signals import post_save
from django.dispatch import receiver

from interview.models import InterviewPassed
from jobboard.tasks import send_email
from pipeline.tasks import candidate_level_up


@receiver(post_save, sender=InterviewPassed)
def interview_passed(sender, instance, created, **kwargs):
    if not created:
        candidate = instance.candidate
        vacancy = instance.interview.vacancy
        recruiter = instance.recruiter
        action = instance.interview.action

        if instance.duration.seconds >= 600 and not action.chain.approvable:
            candidate_level_up.delay(vacancy.id, candidate.id)

        message = 'Interview for vacancy {} with{} {} was over.'

        send_email.delay(message=message.format(vacancy.title, ' candidate', candidate.full_name or candidate.username),
                         to=recruiter.email)
        send_email.delay(message=message.format(vacancy.title, '', recruiter.full_name or recruiter.username),
                         to=candidate.email)

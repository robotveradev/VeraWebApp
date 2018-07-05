from django.db.models.signals import post_save
from django.dispatch import receiver

from interview.models import InterviewPassed
from jobboard.tasks import send_email


@receiver(post_save, sender=InterviewPassed)
def interview_passed(sender, instance, created, **kwargs):
    if created:
        candidate = instance.candidate
        vacancy = instance.interview.vacancy
        employer = instance.interview.employer

        message = 'Interview for vacancy {} with {} {} was over'

        send_email.delay(message=message.format(vacancy.title, 'candidate', candidate.full_name),
                         to=employer.user.email)
        send_email.delay(message=message.format(vacancy.title, 'employer', employer.full_name),
                         to=candidate.user.email)

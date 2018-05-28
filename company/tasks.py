from __future__ import absolute_import, unicode_literals

import random
import time

from celery import shared_task

from company.models import Company


@shared_task
def verify_company(company_id):
    """Must set company.verified = True if company verified successfully"""
    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        pass
    else:
        time.sleep(random.randint(0, 100))
        company.verified = True
        company.save()
    return True

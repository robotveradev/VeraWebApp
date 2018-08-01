from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vera.settings')

assert settings.COINBASE_PASSWORD_SECRET != '', 'Coinbase password not provider'

app = Celery('vera')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_transactions': {
        'task': 'CheckTransaction',
        'schedule': 10.0,
    },
}
app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

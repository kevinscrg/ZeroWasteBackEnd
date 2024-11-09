from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Setează setările proiectului Django pentru Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zerowaste.settings')  # calea către settings.py din interiorul aplicației

app = Celery('zerowaste')  # numele aplicației Celery

# Încarcă setările din Django folosind namespace-ul 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descoperă automat task-urile din toate aplicațiile Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

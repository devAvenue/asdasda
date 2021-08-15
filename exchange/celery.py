import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchange.settings')

app = Celery('exchange')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_address': {
        'task': 'app.tasks.check_address',
        'schedule': 5
    },
    'check_eth': {
        'task': 'app.tasks.check_eth',
        'schedule': 5
    },
    'check_usdt': {
        'task': 'app.tasks.check_usdt',
        'schedule': 5
    },
    'check_bch': {
        'task': 'app.tasks.check_bch',
        'schedule': 5
    },
    'new_statistic': {
        'task': 'app.tasks.new_statistic',
        'schedule': crontab(minute=0, hour=0)
    },
}

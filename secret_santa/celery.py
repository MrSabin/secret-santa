import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secret_santa.settings')
app = Celery('secret_santa')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'user_notification_everyday': {
        'task': 'tg_bot.tasks.start_game',
        # 'schedule': crontab(minute='0', hour='0'),
        # for test use this
        'schedule': crontab(minute='*'),
    }
}

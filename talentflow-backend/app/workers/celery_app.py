from celery import Celery
from kombu import Queue, Exchange
from app.config import settings

app = Celery('talentflow')
app.config_from_object({
    'broker_url':                  settings.REDIS_URL,
    'result_backend':              settings.REDIS_URL,
    'task_serializer':             'json',
    'accept_content':              ['json'],
    'timezone':                    'UTC',
    'task_acks_late':              True,
    'task_reject_on_worker_lost':  True,
    'worker_prefetch_multiplier':  1,
    'task_soft_time_limit':        300,   # 5 min soft limit
    'task_time_limit':             360,   # 6 min hard limit
    'task_max_retries':            3,
    'task_default_retry_delay':    30,    # seconds
    'worker_max_tasks_per_child':  500,   # Recycle to prevent memory leak
    'task_routes': {
        'app.workers.cv_tasks.*':           {'queue': 'cv_processing'},
        'app.workers.report_tasks.*':       {'queue': 'reporting'},
        'app.workers.notification_tasks.*': {'queue': 'notifications'},
    },
    'task_queues': (
        Queue('cv_processing',  Exchange('cv_processing'),  routing_key='cv', priority=10),
        Queue('reporting',      Exchange('reporting'),      routing_key='report', priority=5),
        Queue('notifications',  Exchange('notifications'),  routing_key='notify', priority=1),
    ),
})

app.autodiscover_tasks(['app.workers.cv_tasks', 'app.workers.notification_tasks'])

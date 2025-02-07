from celery import Celery


celery_app = Celery(
    'src',
    broker='amqp://guest:guest@localhost:5672',
    backend='rpc://',
)

celery_app.conf.update(
    task_routes={
        'app.tasks.send_email': 'default',
    }
)
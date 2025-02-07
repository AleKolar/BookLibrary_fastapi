from celery import Celery


def make_celery():
    app = Celery(
        'src',
        broker='amqp://guest:guest@localhost:5672',  # URL сообщения брокера
        backend='rpc://'  # Бэкенд для подсчета результатов
    )

    app.conf.update(
        task_routes={
            'app.tasks.send_email': 'default',
        },
    )

    return app

celery_app = make_celery()
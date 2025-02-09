
from celery import Celery

def make_celery():
    app_task = Celery(
        'src',
        broker='amqp://guest:guest@localhost:5672',
        backend='rpc://',
    )

    # Обновляем конфигурацию
    app_task.conf.update(
        task_routes={
            'src.src_celery.tasks.send_email': 'default',
        },
        broker_connection_retry_on_startup=True,  # Добавлено для попыток повторного подключения
    )

    with app_task.connection() as connection:
        app_task.loader.import_module('src.src_celery.tasks')

    return app_task

celery_app = make_celery()
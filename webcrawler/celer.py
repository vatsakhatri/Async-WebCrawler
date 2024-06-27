from celery import Celery
import os
capp=Celery('myapp',broker='redis://localhost:6379/0',backend='redis://localhost:6379/0')

capp.conf.imports=('tasks',)

capp.conf.task_queues={
    'queue1': {
        'exchange': '',         # Default exchange
        'binding_key': 'queue1' # Routing key
    },
    'queue2': {
        'exchange': '',         # Default exchange
        'binding_key': 'queue2' # Routing key
    },
    'default': {
        'exchange': '',         # Default exchange
        'binding_key': 'default' # Routing key
    }
}
capp.conf.task_default_queue = 'default'
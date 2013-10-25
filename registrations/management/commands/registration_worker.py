import zmq
import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from registrations.models import Registration
from registrations import handlers
from registrations import tasks

class Command(BaseCommand):

    def log(self, message):
        f = open(settings.TASK_LOG_PATH, 'a')
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        log_message = "%s\t%s\n" % (now, message)
        self.stdout.write(log_message)
        f.write(log_message)
        f.close()

    def handle(self, *args, **options):
        
        context = zmq.Context() 
        pull_socket = context.socket(zmq.PULL) 
        pull_socket.bind('tcp://*:7002') 
        self.log("Registration Worker ZMQ Socket Bound to 7002")
        
        while True:
            try: 
                data = pull_socket.recv_json() 
                task_name = data.pop('task')
                task_kwargs = data.pop('kwargs')
                self.log("Got task '%s' with kwargs: %s" % (task_name, task_kwargs))
                if hasattr(tasks, task_name):
                    result = getattr(tasks, task_name)(**task_kwargs)
                    self.log("Task '%s' result: %s" % (task_name, result))
                else:
                    self.log("Received unknown task: %s", task_name)
            except Exception, e: 
                self.log("Error: %s" % e)

        pull_socket.close()
        context.term()

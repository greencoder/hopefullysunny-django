import logging
from optparse import make_option
from time import sleep
import sys, os, signal
import traceback

import beanstalkc

from django.conf import settings
from django.core.management.base import NoArgsCommand
from vendor.django_beanstalkd import connect_beanstalkd, BeanstalkError

BEANSTALK_JOB_NAME = getattr(settings, 'BEANSTALK_JOB_NAME', '%(app)s.%(job)s')
BEANSTALK_JOB_FAILED_RETRY = getattr(settings, 'BEANSTALK_JOB_FAILED_RETRY', 3)
BEANSTALK_DISCONNECTED_RETRY_AFTER = getattr(
        settings, 'BEANSTALK_DISCONNECTED_RETRY_AFTER', 30)

logger = logging.getLogger('django_beanstalkd')
logger.addHandler(logging.StreamHandler())

class Command(NoArgsCommand):
    help = "Start a Beanstalk worker serving all registered Beanstalk jobs"
    __doc__ = help
    can_import_settings = True
    requires_model_validation = True
    option_list = NoArgsCommand.option_list + (
        make_option('-w', '--workers', action='store', dest='worker_count',
                    default='1', help='Number of workers to spawn.'),
        make_option('-l', '--log-level', action='store', dest='log_level',
                    default='info', help='Log level of worker process (one of '
                    '"debug", "info", "warning", "error")'),
        make_option('-m', '--module', action='store', dest='module',
                    default='', help='Module to load beanstalk_jobs from'),
    )
    children = [] # list of worker processes
    jobs = {}

    def handle_noargs(self, **options):
        # set log level
        logger.setLevel(getattr(logging, options['log_level'].upper()))

        # find beanstalk job modules
        bs_modules = []
        if not options['module']:
            for app in settings.INSTALLED_APPS:
                try:
                    bs_modules.append(__import__("%s.beanstalk_jobs" % app))
                except ImportError:
                    pass
        else:
            bs_modules.append(__import__("%s.beanstalk_jobs" % options["module"]))
        if not bs_modules:
            logger.error("No beanstalk_jobs modules found!")
            return

        # find all jobs
        jobs = []
        beanstalk_options = {}
        for bs_module in bs_modules:
            try:
                jobs += bs_module.beanstalk_job_list
                beanstalk_options.update(bs_module.beanstalk_jobs.beanstalk_options)
            except AttributeError:
                pass
        if not jobs:
            logger.error("No beanstalk jobs found!")
            return
        self.beanstalk_options = beanstalk_options
        logger.info("Available jobs:")
        workers = {'default': {}}
        for job in jobs:
            # determine right name to register function with
            app = job.app
            jobname = job.__name__
            func = BEANSTALK_JOB_NAME % {
                    'app': app, 'job': jobname}
            try:
                workers[job.worker][func] = job
            except KeyError:
                workers[job.worker] = {func: job}
            logger.info("* %s" % func)

        # spawn all workers and register all jobs
        try:
            worker_count = int(options['worker_count'])
            assert(worker_count > 0)
        except (ValueError, AssertionError):
            worker_count = self.get_workers_count('default')

        self.register_sigterm_handler()
        self.spawn_workers(workers, worker_count)

        # start working
        logger.info("Starting to work... (press ^C to exit)")
        try:
            for child in self.children:
                os.waitpid(child, 0)
        except KeyboardInterrupt:
            sys.exit(0)

    def get_workers_count(self, worker):
        return self.beanstalk_options.get('workers', {}).get(worker, 1)

    def register_sigterm_handler(self):
        """Stop child processes after receiving SIGTERM"""
        def handler(sig, func=None):
            for child in self.children:
                os.kill(child, signal.SIGINT)
            sys.exit(0)
        signal.signal(signal.SIGTERM, handler)

    def spawn_workers(self, workers, worker_count):
        """
        Spawn as many workers as desired (at least 1).
        Accepts:
        - workers, {'default': job_list}
        - worker_count, positive int
        """
        # no need for forking if there's only one worker
        job_list = workers.pop('default')
        if worker_count == 1 and not workers:
            return BeanstalkWorker('default', job_list).work()

        # spawn children and make them work (hello, 19th century!)
        def make_worker(name, jobs):
            child = os.fork()
            if child:
                self.children.append(child)
            else:
                BeanstalkWorker(name, jobs).work()
        if job_list:
            for i in range(worker_count):
                make_worker('default', job_list)
        for key, job_list in workers.items():
            for i in range(self.get_workers_count(key)):
                make_worker(key, job_list)
        logger.info("Spawned %d workers" % len(self.children))

class BeanstalkWorker(object):
    def __init__(self, name, jobs):
        self.name = name
        self.jobs = jobs

    def work(self):
        """children only: watch tubes for all jobs, start working"""
        self.init_beanstalk()

        while True:
            try:
                self._worker()
            except KeyboardInterrupt:
                sys.exit(0)
            except beanstalkc.SocketError, e:
                logger.error("disconnected: %s" % e)
                sleep(BEANSTALK_DISCONNECTED_RETRY_AFTER)
                try:
                    self.init_beanstalk()
                except BeanstalkError, e:
                    logger.error("reconnection failed: %s" % e)
                else:
                    logger.debug("reconnected")
            except Exception, e:
                logger.exception(e)

    def init_beanstalk(self):
        self._beanstalk = connect_beanstalkd()
        for job in self.jobs.keys():
            self._beanstalk.watch(job)
        self._beanstalk.ignore('default')

    def _worker(self):
        job = self._beanstalk.reserve()
        job_name = job.stats()['tube']
        if job_name in self.jobs:
            logger.debug("j:%s, %s(%s)" % (job.jid, job_name, job.body))
            try:
                self.jobs[job_name](job.body)
            except KeyboardInterrupt:
                raise
            except:
                tp, value, tb = sys.exc_info()
                logger.error('Error while calling "%s" with arg "%s": '
                    '%s' % (job_name, job.body, value)
                )
                logger.debug("%s:%s" % (tp.__name__, value))
                logger.debug("\n".join(traceback.format_tb(tb)))
                releases = job.stats()['releases']
                if releases >= BEANSTALK_JOB_FAILED_RETRY:
                    logger.info('j:%s, failed->bury' % job.jid)
                    job.bury()
                    return
                else:
                    delay = releases * 60
                    logger.info('j:%s, failed->retry with delay %ds' % (job.jid, delay))
                    job.release(delay=delay)
            else:
                logger.debug("j:%s, done->delete" % job.jid)
                job.delete()
                return
        else:
            job.release()

class _beanstalk_job(object):
    """
    Decorator marking a function inside some_app/beanstalk_jobs.py as a
    beanstalk job
    """

    def __init__(self, f, worker):
        self.f = f
        self.__name__ = f.__name__
        self.worker = worker
        
        # determine app name
        parts = f.__module__.split('.')
        if len(parts) > 1:
            self.app = parts[-2]
        else:
            self.app = ''

        # store function in per-app job list (to be picked up by a worker)
        bs_module = __import__(f.__module__)
        try:
            if self not in bs_module.beanstalk_job_list:
                bs_module.beanstalk_job_list.append(self)
        except AttributeError:
            bs_module.beanstalk_job_list = [self]

    def __call__(self, arg):
        # call function with argument passed by the client only
        return self.f(arg)

def beanstalk_job(func=None, worker="default"):
    def decorator(func):
        return _beanstalk_job(func, worker)
    return decorator(func) if func else decorator

from vendor.django_beanstalkd import beanstalk_job

beanstalk_options = {
    "workers": {"forecasts": 5}
}

@beanstalk_job(worker='forecasts')
def job_send_forecast_email(arg):
    print "Send forecast email"

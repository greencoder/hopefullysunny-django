from vendor.django_beanstalkd import beanstalk_job

from forecasts.handlers import send_forecast_email
from registrations.models import Registration

beanstalk_options = {
    "workers": {"forecasts": 3}
}

@beanstalk_job(worker='forecasts')
def job_send_forecast_email(arg):
    
    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        print "Could not find registration id %d" % int(arg)
        return False

    success = send_forecast_email(registration)
    return success

from django.conf import settings
from vendor.django_beanstalkd import beanstalk_job

from forecasts.handlers import send_forecast_email
from registrations.models import Registration

beanstalk_options = {
    "workers": {"forecasts": 3}
}

def log(job_name, message):
    
    log_msg = "%s\t%s\t%s" % (datetime.datetime.now(), job_name, message)
    print log_msg

    f = open(settings.BEANSTALK_LOG_FILE, 'a')
    f.write(log_msg + "\n")
    f.close()


@beanstalk_job(worker='forecasts')
def job_send_forecast_email(arg):
    
    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        log("job_send_forecast_email", "Could not find registration id %d" % int(arg))
        return False

    success = send_forecast_email(registration)
    log("job_send_forecast_email_link", "Sent forecast email to %s" % registation.email)
    return success

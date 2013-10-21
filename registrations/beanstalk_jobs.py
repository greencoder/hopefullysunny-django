import datetime

from django.conf import settings
from vendor.django_beanstalkd import beanstalk_job

from registrations.models import Registration
from registrations.handlers import send_email_confirmation
from registrations.handlers import send_email_update_link
from registrations.handlers import geocode_zip

beanstalk_options = {
    "workers": {"registrations": 5}
}

def log(job_name, message):
    
    log_msg = "%s\t%s\t%s" % (datetime.datetime.now(), job_name, message)
    print log_msg

    f = open(settings.BEANSTALK_LOG_FILE, 'a')
    f.write(log_msg + "\n")
    f.close()

@beanstalk_job(worker='registrations')
def job_send_update_email_link(arg):

    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        log("job_send_update_email", "Could not find registration id %d" % int(arg))
        return False

    success = send_email_update_link(registration)
    log("job_send_update_email_link", "Sent email update link for %s" % registation.email)
    return success


@beanstalk_job(worker='registrations')
def job_geocode_zip(arg):
    
    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        log("job_geocode_zip", "Could not find registration id %d" % int(arg))
        return False

    success = geocode_zip(registration)
    log("job_geocode_zip", "Geocoded zip %s" % registration.zip_code)
    return success


@beanstalk_job(worker='registrations')
def job_send_email_confirmation(arg):

    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        log("job_send_email_confirmation", "Could not find registration id %d" % int(arg))
        return False

    success = send_email_confirmation(registration)
    log("job_send_email_confirmation", "Sent email confirmation to %s" % registration.email)
    return success


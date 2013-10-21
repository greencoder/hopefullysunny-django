from vendor.django_beanstalkd import beanstalk_job

from registrations.models import Registration

from registrations.handlers import send_email_confirmation
from registrations.handlers import send_email_update_link
from registrations.handlers import geocode_zip

beanstalk_options = {
    "workers": {"registrations": 5}
}

@beanstalk_job(worker='registrations')
def job_send_update_email_link(arg):

    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        print "Could not find registration id %d" % int(arg)
        return False

    success = send_email_update_link(registration)
    return success


@beanstalk_job(worker='registrations')
def job_geocode_zip(arg):
    
    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        print "Could not find registration id %d" % int(arg)
        return False

    success = geocode_zip(registration)
    return success


@beanstalk_job(worker='registrations')
def job_send_email_confirmation(arg):

    try:
        registration = Registration.objects.get(id=int(arg))
    except Registration.DoesNotExist:
        print "Could not find registration id %d" % int(arg)
        return False

    success = send_email_confirmation(registration)
    return success

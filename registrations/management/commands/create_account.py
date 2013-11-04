import datetime
import sys
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from registrations.models import Registration
from registrations import handlers

class Command(BaseCommand):

    def handle(self, *args, **options):
        
        if len(args) < 2:
            sys.exit("Please provide an email address and zip code.")
        else:
            email = args[0]
            zip_code = args[1]
        
        registration = Registration.signup(email, zip_code)
        
        if not registration:
            sys.exit("Error: that account is already registered.")

        #handlers.geocode_registration(registration)
        registration.fire_geocode_registration_task()
        
        registration.confirmation_email_sent = True
        registration.email_is_confirmed = True
        registration.confirmed_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        registration.updated_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        registration.save()
        
        print "Done."

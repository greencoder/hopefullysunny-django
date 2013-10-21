import datetime
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from forecasts.lib.forecast import Forecast
from registrations.models import Registration
from registrations.handlers import geocode_zip

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

        geocode_zip(registration)
        
        registration.confirmation_email_sent = True
        registration.email_is_confirmed = True
        registration.confirmed_at = datetime.datetime.now()
        registration.updated_at = datetime.datetime.now()
        registration.save()
        
        print "Done."

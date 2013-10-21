# -*- coding: utf-8 -*-

import requests
import sys

from django.core.management.base import BaseCommand, CommandError

from registrations.models import Registration
from forecasts.handlers import send_forecast_email as forecast_handler

class Command(BaseCommand):

    def handle(self, *args, **options):

        if len(args) == 0:
            sys.exit("Please specify a registered email account.")
        else:
            email = args[0]

        registration = Registration.objects.get(email=email)
        success = forecast_handler(registration)
        
        if success:
            print "Forecast Email Sent: %s" % registration.email
        else:
            print "Error sending email."
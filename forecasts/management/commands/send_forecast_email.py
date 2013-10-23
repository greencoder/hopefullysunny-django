# -*- coding: utf-8 -*-

import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

from registrations.models import Registration
from forecasts import handlers
from forecasts.lib.forecast import Forecast

class Command(BaseCommand):

    def handle(self, *args, **options):

        if len(args) == 0:
            sys.exit("Please specify a registered email account.")
        else:
            email = args[0]

        try:
            registration = Registration.objects.get(email=email, status=1)
        except Registration.DoesNotExist:
            sys.exit("Registration not found.")

        cache_key = "%s,%s" % (registration.latitude, registration.longitude)
        forecasts_list = cache.get(cache_key)

        # If we don't have a value, it was not found in the cache. Look up and cache it.
        if not forecasts_list:
            forecasts_list = Forecast.get_forecast(registration.latitude, registration.longitude)
            print "Caching the fetched forecasts"
            cache.set(cache_key, forecasts_list, 3600)

        success = handlers.send_forecast_email(registration, forecasts_list)
        
        if success:
            print "Forecast Email Sent: %s" % registration.email
        else:
            print "Error sending email."
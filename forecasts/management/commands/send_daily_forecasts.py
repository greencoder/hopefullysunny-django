# -*- coding: utf-8 -*-

import sys
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

from registrations.models import Registration
from forecasts import handlers
from forecasts.lib.forecast import Forecast

class Command(BaseCommand):

    def handle(self, *args, **options):

        print "Starting Daily Email Run: %s" % datetime.datetime.now()

        for registration in Registration.objects.filter(status=1, latitude__isnull=False,
            longitude__isnull=False):

            cache_key = "%.2f,%.2f" % (registration.latitude, registration.longitude)
            forecasts_list = cache.get(cache_key)
            
            # If we don't have a value, it was not found in the cache. Look up and cache it.
            if not forecasts_list:
                forecasts_list = Forecast.get_forecast(registration.latitude, registration.longitude)
                print "Caching the fetched forecasts for %s" % cache_key
                cache.set(cache_key, forecasts_list, 3600)

            success = handlers.send_forecast_email(registration, forecasts_list)

            if success:
                print "Forecast Email Sent: %s" % registration.email
            else:
                print "Error sending email."
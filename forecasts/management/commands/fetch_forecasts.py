import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.cache import cache

from forecasts.lib.forecast import Forecast
from registrations.models import Registration

class Command(BaseCommand):

    def chunks(self, list, chunk_size):
        """ Yield successive chunks from a list """
        for i in xrange(0, len(list), chunk_size):
            yield list[i:i+chunk_size]

    def handle(self, *args, **options):

        latlong_list = []
        for registration in Registration.objects.filter(status=1):
            # Check the cache to see if this lat/long has already been fetched.
            cache_key = "%.2f,%.2f" % (registration.latitude, registration.longitude)
            entry = cache.get(cache_key)
            if not entry:
                print "Location not in cache. Adding to lookup list: %s" % cache_key
                latlong = (registration.latitude, registration.longitude)
                latlong_list.append(latlong)
        
        # Now that we have a list of all the lat/long tuples we need to look up, 
        # let's cut them into chunks of 200 (the max the service allows)
        for chunk in self.chunks(latlong_list, 200):        
            location_forecasts = Forecast.get_multiple_forecasts(chunk)
            for location in location_forecasts:
                latlong = location['location']
                forecasts = location['forecasts']
                cache_key = "%s,%s" % (latlong[0], latlong[1])
                print "Caching forecast for %s, %s" % (latlong[0], latlong[1])
                cache.set(cache_key, forecasts, 3600)

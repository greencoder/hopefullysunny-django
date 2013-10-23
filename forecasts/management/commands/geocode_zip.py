import sys
from optparse import make_option
import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from forecasts.handlers import Forecast

class Command(BaseCommand):

    def handle(self, *args, **options):

        if not len(args) == 1:
            sys.exit("You must specify a zip code.")

        request = requests.get('http://geocoder.us/service/json/geocode?zip=%s' % args[0])

        if request.ok:
            data = request.json()[0]
            print data['city'], data['state'], data['lat'], data['long']
        else:
            print "Error geocoding zip code: %s" % options['zip_code']

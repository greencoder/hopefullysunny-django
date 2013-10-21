from optparse import make_option
import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from forecasts.handlers import Forecast

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--zip', type="string", dest='zip_code', default=None, help='Zip Code'),
    )

    def handle(self, *args, **options):

        request = requests.get('http://geocoder.us/service/json/geocode?zip=%s' % options['zip_code'])

        if request.ok:
            data = request.json()[0]
            print data['city'], data['state'], data['lat'], data['long']
        else:
            print "Error geocoding zip code: %s" % options['zip_code']

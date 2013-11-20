import sys
#from optparse import make_option
import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from geocoder.models import Zipcode

class Command(BaseCommand):

    def handle(self, *args, **options):

        if not len(args) == 1:
            sys.exit("You must specify a zip code.")

        try:
            z = Zipcode.objects.get(postal_code=args[0])
            sys.stdout.write("%s, %s, %s, %s\n" % (z.place_name, z.admin_code1, z.latitude, z.longitude))
        except Zipcode.DoesNotExist:
            sys.stdout.write("Error geocoding zip code: %s\n" % args[0])

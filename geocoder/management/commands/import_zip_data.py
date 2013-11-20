import zipfile
import StringIO
import sys
import requests
import os
import codecs

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from geocoder.models import Zipcode

class Command(BaseCommand):

    def handle(self, *args, **options):

        tmp_dir = os.path.join(settings.SITE_ROOT, 'geocoder/tmp/')
        data_filepath = os.path.join(tmp_dir, 'US.txt')
        
        if not os.path.exists(tmp_dir):
            sys.exit("Error: Temporary directory does not exist at %s" % tmp_dir)

        if not os.path.exists(data_filepath):
            sys.stdout.write("Downloading US Zip Code Data from Geonames.org\n")
            request = requests.get('http://download.geonames.org/export/zip/US.zip')
            z = zipfile.ZipFile(StringIO.StringIO(request.content))
            z.extractall(tmp_dir)
        else:
            sys.stdout.write("Found data file on disk. Not downloading.\n")
        
        # Delete all existing entries
        sys.stdout.write("Deleting all zip code entries.\n")
        Zipcode.objects.all().delete()
        
        f = codecs.open(data_filepath, encoding='UTF-8')
        contents = f.readlines()
        f.close()
        
        for line in contents:

            data = line.strip().split("\t")

            if len(data) < 11:
                sys.exit(line)

            z = Zipcode.objects.create(
                country_code = data[0],
                postal_code = data[1],
                place_name = data[2],
                admin_name1 = data[3],
                admin_code1 = data[4],
                admin_name2 = data[5],
                admin_code2 = data[6],
                admin_name3 = data[7],
                admin_code3 = data[8],
                latitude =  float(data[9]),
                longitude = float(data[10]),
            )
            
            sys.stdout.write("Added %s\n" % data[1])

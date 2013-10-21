# -*- coding: utf-8 -*-

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from forecasts.lib.forecast import Forecast

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--lat', type="float", dest='lat', default=None, help='Latitude'),
        make_option('--lng', type="float", dest='lng', default=None, help='Latitude'),
    )

    def handle(self, *args, **options):

        forecasts_list = Forecast.get_forecast(options['lat'], options['lng'])
        
        for forecast in forecasts_list:
            print "%s\t%s  %.0f%s-%.0f%s\t%s" % (
                forecast['date'].strftime("%a"),
                forecast['code'], 
                forecast['min_temp'], 
                u'°', 
                forecast['max_temp'], 
                u'°', 
                forecast['condition']
            )

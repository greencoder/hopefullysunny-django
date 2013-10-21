# -*- coding: utf-8 -*-

import requests
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.loader import render_to_string

from forecasts.lib.forecast import Forecast
from registrations.models import Registration

class Command(BaseCommand):

    def handle(self, *args, **options):

        if len(args) == 0:
            sys.exit("Please specify a registered email account.")
        else:
            email = args[0]

        reg = Registration.objects.get(email=email)

        forecasts_list = Forecast.get_forecast(reg.latitude, reg.longitude)

        text_body = render_to_string("email.txt", {
            "forecasts": forecasts_list,
            "registration": reg,
        })

        html_body = render_to_string("email.html", {
            "forecasts": forecasts_list,
            "registration": reg,
        })
        
        today = forecasts_list[0]
        subject = u"Today in %s, %s: %s  %.0f° - %.0f°, %s" % (reg.city, reg.state, today['code'], 
            today['min_temp'], today['max_temp'], today['condition'])

        request = requests.post(settings.MAILGUN_URL, auth=("api", settings.MAILGUN_API_KEY), 
            data={
                "from": "Hopefully Sunny <weather@hopefullysunny.us>",
                  "to": [reg.email,],
                  "h:Reply-To": "hopefullysunnyapp@gmail.com",
                  "subject": subject,
                  "text": text_body,
                  "html": html_body,
            })
        
        print "Email sent."

# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.template.loader import render_to_string

from forecasts.lib.forecast import Forecast

def send_mailgun_email(subject, html_message, text_message, from_addr, to_addr_list):

    request = requests.post(settings.MAILGUN_URL, auth=("api", settings.MAILGUN_API_KEY), 
        data={
            "from": from_addr,
              "to": to_addr_list,
              "h:Reply-To": "hopefullysunnyapp@gmail.com",
              "subject": subject,
              "text": text_message,
              "html": html_message,
        })

    if request.status_code == 200:
        return True
    else:
        return False

def send_forecast_email(registration, forecasts_list): 

    text_message = render_to_string("email.txt", {
        "forecasts": forecasts_list,
        "registration": registration,
    })

    html_message = render_to_string("email.html", {
        "forecasts": forecasts_list,
        "registration": registration,
    })
    
    today = forecasts_list[0]
    subject = u"%s  %.0f°, %.0f°, %s" % (today['code'], today['max_temp'], 
        today['min_temp'], today['condition'])

    success = send_mailgun_email(subject, html_message, text_message,
        'Hopefully Sunny <weather@hopefullysunny.us>', [registration.email,])
    
    return success

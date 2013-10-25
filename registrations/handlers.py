import requests

from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.loader import render_to_string

def send_mailgun_email(subject, html_message, text_message, from_addr, to_addr_list):
    request = requests.post(settings.MAILGUN_URL, auth=("api", settings.MAILGUN_API_KEY), 
        data = {
            "from": from_addr,
              "to": to_addr_list,
              "h:Reply-To": "hopefullysunnyapp@gmail.com",
              "subject": subject,
              "text": text_message,
              "html": html_message,
        }, timeout=5.0)
    if request.status_code == 200:
        return True
    else:
        return False

def validate_email(email):
    request = requests.get(
        "https://api.mailgun.net/v2/address/validate",
        auth=("api", settings.MAILGUN_PUBLIC_API_KEY),
        params={"address": email}, 
        timeout=5.0,
    )
    return request.ok

def send_confirmation_email(registration):
    
    html_message = render_to_string('confirmation_email.tpl.html', {
        'confirmation_link': reverse('signup-confirm', kwargs={'uuid': registration.uuid}),
    })
    
    text_message = render_to_string('confirmation_email.tpl.txt', {
        'confirmation_link': reverse('signup-confirm', kwargs={'uuid': registration.uuid}),
    })
    
    success = send_mailgun_email('Hopefully Sunny Email Confirmation', html_message, text_message, 
        'Hopefully Sunny <weather@hopefullysunny.us>', [registration.email,])

    if success:
        registration.confirmation_email_sent = True
        registration.save()
        return True
    else:
        return False


def send_update_link_email(registration): 

    html_message = render_to_string('update_email.tpl.html', {
        'update_link': reverse('update-data', kwargs={'uuid': registration.uuid}),
        'registration': registration,        
    })

    text_message = render_to_string('update_email.tpl.txt', {
        'update_link': reverse('update-data', kwargs={'uuid': registration.uuid}),
        'registration': registration,
    })

    success = send_mailgun_email('Hopefully Sunny Preferences Update', html_message, text_message,
        'Hopefully Sunny <weather@hopefullysunny.us>', [registration.email,])
    
    return success

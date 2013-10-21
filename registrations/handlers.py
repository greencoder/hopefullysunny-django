import requests

from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.loader import render_to_string

regions_by_state = {
    'AL': 'Central',    'AK': 'Pacific',
    'AZ': 'Mountain',   'AR': 'Central',
    'CA': 'Pacific',    'CO': 'Mountain',
    'CT': 'Eastern',    'DE': 'Eastern',
    'DC': 'Eastern',    'FL': 'Eastern',
    'GA': 'Eastern',    'HI': 'Pacific',
    'ID': 'Mountain',   'IL': 'Central',
    'IN': 'Eastern',    'IA': 'Central',
    'KS': 'Central',    'KY': 'Central',
    'LA': 'Central',    'ME': 'Eastern',
    'MD': 'Eastern',    'MA': 'Eastern',
    'MI': 'Eastern',    'MN': 'Central',
    'MS': 'Central',    'MO': 'Central',
    'MT': 'Mountain',   'NE': 'Central',
    'NV': 'Pacific',    'NH': 'Eastern',
    'NJ': 'Eastern',    'NM': 'Mountain',
    'NY': 'Eastern',    'NC': 'Eastern',
    'ND': 'Central',    'OH': 'Eastern',
    'OK': 'Central',    'OR': 'Pacific',
    'PA': 'Eastern',    'RI': 'Eastern',
    'SC': 'Eastern',    'SD': 'Central',
    'TN': 'Central',    'TX': 'Central',
    'UT': 'Mountain',   'VA': 'Eastern',
    'VT': 'Eastern',    'WA': 'Pacific',
    'WV': 'Eastern',    'WI': 'Central',
    'WY': 'Mountain',   'AS': 'Pacific',
    'GU': 'Pacific',    'MP': 'Pacific',
    'PR': 'Atlantic',   'VI': 'Atlantic',
    'UM': 'Pacific',    'FM': 'Pacific',
    'MH': 'Pacific',    'PW': 'Pacific',
}

region_ids = {
    'Unknown': 0,
    'Atlantic': 1,
    'Eastern': 2,
    'Central': 3,
    'Mountain': 4,
    'Pacific': 5,
}

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

def send_email_confirmation(registration):
    
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


def send_email_update_link(registration): 

    html_message = render_to_string('update_email.tpl.html', {
        'update_link': reverse('update-data', kwargs={'uuid': registration.uuid}),
    })

    text_message = render_to_string('update_email.tpl.txt', {
        'update_link': reverse('update-data', kwargs={'uuid': registration.uuid}),
    })

    success = send_mailgun_email('Hopefully Sunny Preferences Update', html_message, text_message,
        'Hopefully Sunny <weather@hopefullysunny.us>', [registration.email,])
    
    if success:
        return True
    else:
        return False


def geocode_zip(registration):

    request = requests.get('http://geocoder.us/service/json/geocode?zip=%s' % registration.zip_code)

    if request.ok:
        data = request.json()[0]
        registration.state = data['state']
        registration.city = data['city']
        registration.latitude = data['lat']
        registration.longitude = data['long']
        
        try:
            region = regions_by_state[data['state']]
            registration.region = region_ids[region]
        except KeyError:
            registration.region = 0 # Unknown
        
        registration.save()
        return True
    else:
        print "Error geocoding zip code: %s" % registration.zip_code
        return False

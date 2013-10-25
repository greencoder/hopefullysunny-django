import requests

from django.conf import settings

from registrations.models import Registration

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

def geocode_registration(id):

    try:
        registration = Registration.objects.get(id=id)
    except Registration.DoesNotExist:
        print "Could not find registration with ID %s" % id
        return False

    request = requests.get('http://geocoder.us/service/json/geocode?zip=%s' % registration.zip_code)

    if request.status_code == 200:

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

        registration.status = 1 # Confirmed
        registration.save()
        return True

    else:
        return False


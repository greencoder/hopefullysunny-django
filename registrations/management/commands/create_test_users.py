import datetime
import sys
import pytz
import uuid

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
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

capitals = [
    "Montgomery,AL,32.361538,-86.279118",
    "Juneau,AK,58.301935,-134.419740",
    "Phoenix,AZ,33.448457,-112.073844",
    "Little Rock,AR,34.736009,-92.331122",
    "Sacramento,CA,38.555605,-121.468926",
    "Denver,CO,39.7391667,-104.984167",
    "Hartford,CT,41.767,-72.677",
    "Dover,DE,39.161921,-75.526755",
    "Tallahassee,FL,30.4518,-84.27277",
    "Atlanta,GA,33.76,-84.39",
    "Honolulu,HI,21.30895,-157.826182",
    "Boise,ID,43.613739,-116.237651",
    "Springfield,IL,39.783250,-89.650373",
    "Indianapolis,IN,39.790942,-86.147685",
    "Des Moines,IA,41.590939,-93.620866",
    "Topeka,KS,39.04,-95.69",
    "Frankfort,KY,38.197274,-84.86311",
    "Baton Rouge,LA,30.45809,-91.140229",
    "Augusta,MA,44.323535,-69.765261",
    "Annapolis,MD,38.972945,-76.501157",
    "Boston,MA,42.2352,-71.0275",
    "Lansing,MI,42.7335,-84.5467",
    "Saint Paul,MN,44.95,-93.094",
    "Jackson,MS,32.320,-90.207",
    "Jefferson City,MO,38.572954,-92.189283",
    "Helana,MT,46.595805,-112.027031",
    "Lincoln,NE,40.809868,-96.675345",
    "Carson City,NV,39.160949,-119.753877",
    "Concord,NH,43.220093,-71.549127",
    "Trenton,NJ,40.221741,-74.756138",
    "Santa Fe,NM,35.667231,-105.964575",
    "Albany,NY,42.659829,-73.781339",
    "Raleigh,NC,35.771,-78.638",
    "Bismarck,ND,48.813343,-100.779004",
    "Columbus,OH,39.962245,-83.000647",
    "Oklahoma City,OK,35.482309,-97.534994",
    "Salem,OR,44.931109,-123.029159",
    "Harrisburg,PA,40.269789,-76.875613",
    "Providence,RI,41.82355,-71.422132",
    "Columbia,SC,34.000,-81.035",
    "Pierre,SD,44.367966,-100.336378",
    "Nashville,TN,36.165,-86.784",
    "Austin,TX,30.266667,-97.75",
    "Salt Lake City,UT,40.7547,-111.892622",
    "Montpelier,VT,44.26639,-72.57194",
    "Richmond,VA,37.54,-77.46",
    "Olympia,WA,47.042418,-122.893077",
    "Charleston,WV,38.349497,-81.633294",
    "Madison,WI,43.074722,-89.384444",
    "Cheyenne,WY,41.145548,-104.802042",
]

class Command(BaseCommand):

    def handle(self, *args, **options):

        for capital in capitals:            
            city,state,lat,lng = capital.split(",")
            region = regions_by_state[state]
            region_id = region_ids[region]
            Registration.objects.create(
                email = "snewman18+%s@gmail.com" % slugify(city),
                city = city,
                state = state,
                zip_code = "00000",
                uuid = uuid.uuid1().hex,
                latitude = lat,
                longitude = lng,
                created_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                updated_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                confirmed_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                status = 1,
                region = region_id,
                confirmation_email_sent = True,
            )

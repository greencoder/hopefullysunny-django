import uuid
import datetime

from django.db import models
from django.core.mail import send_mail

from vendor.django_beanstalkd import BeanstalkClient

client = BeanstalkClient()

REGION_CHOICES = (
    ('0', 'Unknown'),
    ('1', 'Atlantic'),
    ('2', 'Eastern'),
    ('3', 'Central'),
    ('4', 'Mountain'),
    ('5', 'Pacific'),
)

STATUS_CHOICES = (
    (0, 'Unconfirmed'),
    (1, 'Confirmed'),
    (2, 'Waiting List'),
)

class Registration(models.Model):

    email = models.EmailField(unique=True)
    uuid = models.CharField(max_length=50, unique=True)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    zip_code = models.CharField(max_length=11, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=5, blank=True)
    region = models.CharField(max_length=1, choices=REGION_CHOICES, blank=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    confirmation_email_sent = models.BooleanField(default=False)
    status = models.SmallIntegerField(choices=STATUS_CHOICES)

    def fire_forecast_email_task(self):
        client.call('forecasts.job_send_forecast_email', self.id)

    def fire_signup_email_task(self):
        client.call('registrations.job_send_email_confirmation', self.id) 

    def fire_update_email_task(self):
        client.call('registrations.job_send_update_email_link', self.id) 

    def fire_geocode_task(self):
        client.call('registrations.job_geocode_zip', self.id)        
        
    @classmethod
    def unsubscribe(self, uuid):
        try:
            r = Registration.objects.get(uuid=uuid)
            r.delete()
            return True
        except Registration.DoesNotExist:
            return False

    @classmethod
    def confirm_email_address(self, uuid):
        try:
            confirmed_count = Registration.objects.filter(status=1).count()
            r = Registration.objects.get(uuid=uuid)
            
            # We have to limit the count to 1500 right now. If we are at 
            # capacity, put them on the waiting list.
            if confirmed_count < 1500:
                r.status = 1
            else:
                r.status = 2
            
            r.confirmed_at = datetime.datetime.now()
            r.save()
            return r
        except Registration.DoesNotExist:
            return False

    @classmethod
    def signup(self, email, zip_code):
        try:
            r = Registration.objects.get(email=email)
            # If they signed up already but haven't confirmed, they 
            # are probably just trying to resend the confirmation.
            if r.status == 0:
                r.zip_code = zip_code
                r.updated_at = datetime.datetime.now()
                r.save()
                return r
            else:
                return False
        except Registration.DoesNotExist:
            r = Registration.objects.create(
                email = email,
                zip_code = zip_code,
                uuid = uuid.uuid1().hex,
                created_at = datetime.datetime.now(),
                updated_at = datetime.datetime.now(),
                status = 0,
            )
            return r

    def __unicode__(self):
        return self.email
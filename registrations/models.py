import uuid
import datetime
import pytz
import zmq

from django.db import models
from django.core.mail import send_mail

from registrations import handlers

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
)

ctx = zmq.Context() 
task_socket = ctx.socket(zmq.PUSH) 
task_socket.connect('tcp://127.0.0.1:7002')

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

    def send_signup_email(self):
        success = handlers.send_confirmation_email(self)
        return success

    def send_update_email(self):
        success = handlers.send_update_link_email(self)
        return success

    def fire_geocode_registration_task(self):
        task_socket.send_json({'task': 'geocode_registration', 'kwargs': {'id': self.id}})

    @classmethod
    def validate_email(self, email):
        success = handlers.validate_email(email)
        return success
        
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
            r.status = 1
            r.confirmed_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
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
                r.updated_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                r.save()
                return r
            else:
                return False
        except Registration.DoesNotExist:
            r = Registration.objects.create(
                email = email,
                zip_code = zip_code,
                uuid = uuid.uuid1().hex,
                created_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                updated_at = datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                status = 0,
            )
            return r

    def __unicode__(self):
        return self.email
from django.contrib import admin

from registrations.models import Registration

from registrations.actions import resend_confirmation_email
from registrations.actions import send_update_link
from registrations.actions import geocode_registration

class RegistrationAdmin(admin.ModelAdmin):

    actions = [resend_confirmation_email, send_update_link, geocode_registration]
    list_display = ('email', 'confirmation_email_sent', 'status', 'city', 'state', 'zip_code', 'region')
    list_filter = ('region',)
    search_fields = ('email',)

    fieldsets = (
        ('User Information', {
            'fields': ('email','uuid','created_at','updated_at', 'status'),
        }),
        ('Email Information', {
            'fields': ('confirmed_at','cancelled_at','confirmation_email_sent'),
        }),
        ('Location Information', {
            'fields': ('latitude','longitude','zip_code','city','state', 'region'),
        }),
    )

admin.site.register(Registration, RegistrationAdmin)

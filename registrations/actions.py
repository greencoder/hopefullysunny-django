from registrations.handlers import send_email_confirmation
from registrations.handlers import send_email_update_link

def resend_confirmation_email(modeladmin, request, queryset):
    for obj in queryset:
        obj.fire_signup_email_task()
resend_confirmation_email.short_description = "Resend confirmation email(s)"

def send_update_link(modeladmin, request, queryset):
    for obj in queryset:
        obj.fire_update_email_task()
send_update_link.short_description = "Send update link email(s)"

def geocode_registration(modeladmin, request, queryset):
    for obj in queryset:
        obj.fire_geocode_task()
geocode_registration.short_description = "Geocode the registration(s)"

def send_forecast_email(modeladmin, request, queryset):
    for obj in queryset:
        obj.fire_forecast_email_task()
send_forecast_email.short_description = "Send forecast email(s)"
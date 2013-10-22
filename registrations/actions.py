def resend_confirmation_email(modeladmin, request, queryset):
    for obj in queryset:
        obj.send_signup_email()
resend_confirmation_email.short_description = "Resend confirmation email(s)"

def send_update_link(modeladmin, request, queryset):
    for obj in queryset:
        obj.send_update_email()
send_update_link.short_description = "Send update link email(s)"

def geocode_registration(modeladmin, request, queryset):
    for obj in queryset:
        obj.geocode_registration()
geocode_registration.short_description = "Geocode the registration(s)"

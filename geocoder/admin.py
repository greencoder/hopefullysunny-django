from django.contrib import admin

from geocoder.models import Zipcode

class ZipcodeAdmin(admin.ModelAdmin):

    list_display = ('postal_code', 'place_name', 'admin_name1', 'latitude', 'longitude')
    search_fields = ('postal_code',)

admin.site.register(Zipcode, ZipcodeAdmin)

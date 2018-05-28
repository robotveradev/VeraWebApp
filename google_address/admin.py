from django.contrib import admin

from google_address.models import *


class GoogleAddressAdmin(admin.ModelAdmin):
    fields = [
        'id', 'raw', 'raw2'
    ]

    list_display = [
        'id', 'raw', 'raw2'
    ]

    list_filter = []

    list_editable = []

    search_fields = ['raw', 'raw2', 'address_line']

    readonly_fields = [
        'id'
    ]

    raw_id_fields = []


admin.site.register(Address, GoogleAddressAdmin)
admin.site.register(AddressComponentType)
admin.site.register(AddressComponent)

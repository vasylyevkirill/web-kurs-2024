from django.contrib import admin
from taxi.models import Car, City, District, Street, Address, Driver, Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue

class AddressAdmin(admin.ModelAdmin):
    raw_id_fields = ('street',)
    search_fields = ['name', 'street__name', 'street__district__name', 'street__district__city__name']


class StreetAdmin(admin.ModelAdmin): 
    raw_id_fields = ('district',)
    search_fields = ['name', 'district__name', 'district__city__name']


class DistrictAdmin(admin.ModelAdmin):
    search_fields = ['name', 'city__name']


class CarAdmin(admin.ModelAdmin):
    list_filter = ('is_ready', 'comfort_class')
    search_fields = ['number', 'color', 'make', 'series']


admin.site.register(Car, CarAdmin)
admin.site.register(City)
admin.site.register(District, DistrictAdmin)
admin.site.register(Street, StreetAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Driver)
admin.site.register(Consumer)
admin.site.register(Ride)
admin.site.register(DriverRate)
admin.site.register(ConsumerRate)
admin.site.register(RideAddressesQueue)

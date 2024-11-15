from django.contrib import admin
from taxi.models import Car, City, District, Street, Address, Driver, Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue


admin.site.register(Car)
admin.site.register(City)
admin.site.register(District)
admin.site.register(Street)
admin.site.register(Address)
admin.site.register(Driver)
admin.site.register(Consumer)
admin.site.register(Ride)
admin.site.register(DriverRate)
admin.site.register(ConsumerRate)
admin.site.register(RideAddressesQueue)

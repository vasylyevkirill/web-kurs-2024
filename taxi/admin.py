from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin

from taxi.models import Car, City, District, Street, Address, Driver, Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue, AbstractTaxiUser


class RideResource(ModelResource):
    class Meta:
        model = Ride
        fields = (
            'consumer', 'driver', 'date_created', 'date_ended', 'addresses'
        )

    def get_dehydrated_average_user(self, user: AbstractTaxiUser) -> dict:
        return {
            'user_id': user.user.id,
            'location': user.location,
            'profile_image': user.profile_image_url,
            'average_rating': user.average_rating,
        }

    def get_export_queryset(self, request): 
        return Ride.objects.non_canceled.all()

    def dehydrate_consumer(self, ride: Ride) -> dict:
        consumer: Consumer = ride.consumer
        return self.get_dehydrated_average_user(consumer)

    def dehydrate_driver(self, ride: Ride) -> dict:
        driver = ride.driver
        return {
            **self.get_dehydrated_average_user(driver), **{'current_car': str(driver.current_car)}
        } if driver else {}


    def get_addresses_count(self, ride: Ride) -> int:
        return ride.addresses.count()

    def dehydrate_addresses(self, ride: Ride) -> int:
        return self.get_addresses_count()


@admin.register(Ride)
class RideAdmin(ImportExportModelAdmin):
    resource_classes = [RideResource]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    raw_id_fields = ('street',)
    search_fields = ['name', 'street__name', 'street__district__name', 'street__district__city__name']


@admin.register(Street)
class StreetAdmin(admin.ModelAdmin): 
    raw_id_fields = ('district',)
    search_fields = ['name', 'district__name', 'district__city__name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    search_fields = ['name', 'city__name']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_filter = ('is_ready', 'comfort_class')
    search_fields = ['number', 'color', 'make', 'series']


admin.site.register(City)
admin.site.register(Driver)
admin.site.register(Consumer)
admin.site.register(DriverRate)
admin.site.register(ConsumerRate)
admin.site.register(RideAddressesQueue)

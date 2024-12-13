from rest_framework import serializers

from taxi.models import (
    Car, City, District, Street, Address, Driver,
    Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue
)


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        lookup_field = 'number'
        fields = 'number color make series is_ready comfort_class'.split()


class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True, source='__str__')

    class Meta:
        model = Address
        fields = 'id name street full_address'.split()


class StreetPreviewSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True, source='__str__')

    class Meta:
        model = Street
        fields = 'id name district full_address'.split()

class StreetSerializer(StreetPreviewSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Street
        fields = 'id name addresses full_address'.split()


class DistrictPreviewSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True, source='__str__')

    class Meta:
        model = District
        fields = 'id name full_address'.split()


class DistrictSerializer(DistrictPreviewSerializer):
    streets = StreetPreviewSerializer(many=True, read_only=True)

    class Meta:
        model = District
        fields = 'id name streets full_address'.split()


class CityPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        lookup_field = 'name'
        model = City
        fields = 'name'.split()


class CitySerializer(serializers.ModelSerializer):
    districts = DistrictPreviewSerializer(many=True, read_only=True)
    class Meta:
        model = City
        fields = 'name districts'.split()


class RideAddressesQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideAddressesQueue
        fields = 'ride address order date_created date_ended'.split()


class RideSerializer(serializers.ModelSerializer):
    adresses = RideAddressesQueueSerializer(many=True)
    class Meta:
        model = Ride
        fields = 'consumer adresses driver date_created date_ended'.split()


class DriverRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverRate
        fields = 'target author ride comment rate date_created'.split()


class ConsumerRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerRate
        fields = 'target author ride comment rate date_created'.split()


class DriverPreviewSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True, source='user.first_name')
    last_name = serializers.CharField(read_only=True, source='user.last_name')
    is_free = serializers.BooleanField(read_only=True)
    location = DistrictPreviewSerializer(many=False)
    average_rating = serializers.DecimalField(read_only=True, max_digits=3, decimal_places=2)

    class Meta:
        model = Driver
        fields = 'first_name last_name location average_rating is_free'.split()


class DriverSerializer(DriverPreviewSerializer):
    current_car = CarSerializer(many=False)

    class Meta:
        model = Driver
        fields = 'first_name last_name location current_car average_rating is_free'.split()

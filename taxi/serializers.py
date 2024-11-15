from rest_framework import serializers

from taxi.models import (
    Car, City, District, Street, Address, Driver,
    Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue
)


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = 'number color make series is_ready comfort_class'.split()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = 'name street'.split()


class StreetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = 'name district addresses'.split()


class DistrictSerializer(serializers.ModelSerializer):
    streets = StreetSerializer(many=True, read_only=True)
    class Meta:
        model = District
        fields = 'name streets city'.split()


class CitySerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)
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

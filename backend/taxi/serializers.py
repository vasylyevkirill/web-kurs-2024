import logging
from django.urls import reverse
from rest_framework import serializers

from taxi.models import (
    Car, City, District, Street, Address, Driver,
    Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue,
    AbstractTaxiUser)


logger = logging.getLogger(__name__)


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        lookup_field = 'number'
        fields = 'number color make series is_ready comfort_class'.split()

class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True, source='__str__')

    class Meta:
        model = Address
        lookup_field = 'id'
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


class AbstractUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True, source='user.first_name')
    last_name = serializers.CharField(read_only=True, source='user.last_name')
    location = DistrictPreviewSerializer(many=False)
    average_rating = serializers.DecimalField(read_only=True, max_digits=3, decimal_places=2)

    class Meta:
        model = AbstractTaxiUser
        fields = 'first_name last_name location profile_image_url'.split()


class ConsumerSerializer(AbstractUserSerializer):
    class Meta:
        model = Consumer
        fields = 'first_name last_name location average_rating profile_image_url'.split()


class DriverPreviewSerializer(AbstractUserSerializer):
    is_free = serializers.BooleanField(read_only=True)

    class Meta:
        model = Driver
        fields = 'first_name last_name location average_rating is_free profile_image_url'.split()


class DriverSerializer(DriverPreviewSerializer):
    current_car = CarSerializer(many=False)

    class Meta:
        model = Driver
        fields = 'first_name last_name location current_car average_rating is_free profile_image_url'.split()


class InlineRideAddressesQueueSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True, source='address.__str__')
    name = serializers.CharField(read_only=True, source='address.name')

    date_created = serializers.DateTimeField(read_only=True)
    date_ended = serializers.DateTimeField(read_only=True)
    order = serializers.IntegerField(read_only=True)

    class Meta:
        model = RideAddressesQueue
        fields = 'full_address name order date_created date_ended'.split()


class RideAddressesQueueSerializer(InlineRideAddressesQueueSerializer):
    ride = serializers.PrimaryKeyRelatedField(queryset=Ride.objects.all(), required=False)

    def is_valid(self, *, raise_exception: bool=True):
        if not hasattr(self, 'inital_data'):
            return super().is_valid(raise_exception=raise_exception)

        ride = self.context.get('ride')
        if 'ride' not in self.initial_data:
            if ride is not None:
                self.initial_data['ride'] = ride
            else:
                raise serializers.ValidationError('Ride field pk not provided in context or data kwarg')


        return super().is_valid(raise_exception=raise_exception)

    class Meta:
        model = RideAddressesQueue
        fields = 'ride address order date_created date_ended full_address name'.split()


class RideCreateSerializer(serializers.ModelSerializer):
    addresses = InlineRideAddressesQueueSerializer(many=True)
    driver = DriverPreviewSerializer(read_only=True)
    consumer = serializers.PrimaryKeyRelatedField(queryset=Consumer.objects.all(), required=False)
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = 'consumer addresses driver date_created date_ended status price id absolute_url'.split()

    def get_absolute_url(self, instance: Ride):
        return reverse('taxi:rides-detail', args=[str(instance.pk)])

    def validate(self, data):
        data = super().validate(data)
        request = self.context.get('request')

        addresses = data.get('addresses')
        if len(addresses) < 2:
            raise serializers.ValidationError(f'At least two addresses but {len(addresses)} given.')
        if not data.get('consumer'):
            if not(request and hasattr(request, 'user') and request.user.is_authenticated and Consumer.objects.filter(user=request.user.id).count()):
                raise serializers.ValidationError('User must be authenticated')

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        consumer = Consumer.objects.get(user=request.user.id if request else validated_data.pop('consumer'))
        addresses = validated_data.pop('addresses')
        instance = Ride.objects.create(**{**validated_data, **{'consumer': consumer}})
        return self.update(instance, {**validated_data, 'addresses': addresses})

    def update(self, instance, validated_data):
        addresses_list = validated_data.pop('addresses')
        instance.addresses.all().delete()

        for address_data in addresses_list:
            address_data['ride'] = instance.id
            address = address_data.get('address')
            address_data['address'] = address.id if isinstance(address, Address) else address

            serializer = RideAddressesQueueSerializer(data=address_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            address_instance = serializer.save()

        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
          
        return instance

class RideSerializer(RideCreateSerializer):
    addresses = InlineRideAddressesQueueSerializer(many=True)
    driver = DriverPreviewSerializer(read_only=True)
    consumer = ConsumerSerializer(read_only=True)


class DriverRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverRate
        fields = 'ride comment rate date_created'.split()


class ConsumerRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerRate
        fields = 'ride comment rate date_created'.split()

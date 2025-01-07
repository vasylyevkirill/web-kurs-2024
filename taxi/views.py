from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from taxi.models import (
    Car, City, District, Street, Address, Driver,
    Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue
)
from taxi.serializers import (
    CitySerializer,
    CityPreviewSerializer,
    DistrictSerializer,
    DistrictPreviewSerializer,
    StreetSerializer,
    StreetPreviewSerializer,
    AddressSerializer,
    CarSerializer,
    DriverSerializer,
    RideSerializer,
    RideAddressesQueueSerializer,
)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name'] 


    def get_serializer_class(self, *args, **kwargs):
        if self.action in 'list '.split():
            return CityPreviewSerializer
        return self.serializer_class


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'full_address']


    def get_serializer_class(self, *args, **kwargs):
        if self.action in 'list '.split():
            return DistrictPreviewSerializer
        return self.serializer_class


class StreetViewSet(viewsets.ModelViewSet):
    queryset = Street.objects.all().select_related('street').prefetch_related('addresses')
    serializer_class = StreetSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'full_address']

    def get_serializer_class(self, *args, **kwargs):
        if self.action in 'list '.split():
            return StreetPreviewSerializer
        return self.serializer_class


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all().select_related('street')
    serializer_class = AddressSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'full_address']


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    pagination_class = LargeResultsSetPagination


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if self.action in 'list '.split():
            return Driver.objects.available()
        return self.queryset

    
    @action(methods=['GET'], detail=False)
    def available(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def get_object(self): 
        if self.action in 'current '.split():
            return self.get_queryset().get(date_ended__isnull=True)
        return super().obj_object()

    @action(methods=['GET'], detail=True)
    def current(self, request, *args, **kwargs):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def accept(self, request):
        driver = None
        if request and hasattr(request, "user") and request.user.is_authenticated and Driver.objects.filter(request.user.id).count():
            driver = request.user
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        instance.driver = driver
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def complete_address(self, request, pk, order=None, *args, **kwargs):
        instance = self.get_object()
        
        pending_addresses = instance.addresses.filter(date_ended__isnull=True)
        response_status=status.HTTP_201_CREATED
        if pending_addresses.count():
            address_queue_instance.date_ended = datetime.now()
            address_queue_instance.save()
        else:
            status = status.HTTP_208_ALREADY_REPORTED
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=response_status)

    @action(methods=['POST'], detail=True)
    def add_address(self, *args, **kwargs):
        return

    @action(methods=['POST'], detail=True)
    def change_address(self, *args, **kwargs):
        return

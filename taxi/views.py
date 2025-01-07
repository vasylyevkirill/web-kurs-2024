from datetime import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, serializers
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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
    RideCreateSerializer,
    RideAddressesQueueSerializer,
)


User = get_user_model()


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

    def get_serializer_class(self) -> serializers.ModelSerializer:
        if self.action in 'add_address ':
            return RideAddressesQueueSerializer
        if self.action in 'create update':
            return RideCreateSerializer
        return self.serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action not in 'list ':
            context['ride'] = self.kwargs.get('pk', None)
        return context

    def get_object(self): 
        if self.action in 'current '.split():
            return self.get_queryset().get(date_ended__isnull=True)
        return super().get_object()

    def get_request_user(self) -> User | None:
        request = self.request
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return request.user
        return None

    def get_request_driver(self) -> Driver | None:
        user = self.get_request_user()
        if user and Driver.objects.filter(user=user.id).count():
            return Driver.objects.get(user=user.id)
        return None

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
    def accept(self, request, *args, **kwargs):
        driver = self.get_request_driver()
        if not driver:
            return Response(status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        instance.driver = driver
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def complete_address(self, request, *args, **kwargs):
        instance = self.get_object()
        driver = self.get_request_driver()

        if not driver or instance.driver != driver:
            return Response(status=status.HTTP_403_FORBIDDEN)
 
        response_status = status.HTTP_200_OK
        if instance.pending_addresses.count():
            instance.complete_address()
        else:
            response_status = status.HTTP_208_ALREADY_REPORTED
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=response_status)

    @action(methods=['POST'], detail=True)
    def add_address(self, *args, **kwargs): 
        instance = self.get_object()
        serializer = self.get_serializer(
            data={**self.request.data, **{'ride': instance.id}}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True)
    def change_address(self, *args, **kwargs):
        return

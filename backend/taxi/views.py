from datetime import datetime

from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, serializers
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters import rest_framework as filters

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
from taxi.forms import DriverRateForm, ConsumerRateForm


User = get_user_model()


def get_request_user(request) -> User | None:
    if request and hasattr(request, "user") and request.user.is_authenticated:
        return request.user
    return None


def get_request_driver(request) -> Driver | None:
    user = get_request_user(request)
    if user and Driver.objects.filter(user=user.id).count():
        return Driver.objects.get(user=user.id)
    return None


def get_request_consumer(request) -> Consumer | None:
    user = get_request_user(request)
    if user and Consumer.objects.filter(user=user.id).count():
        return Consumer.objects.get(user=user.id)
    return None


def available_rides_view(request):
    latest_rides = Ride.objects.available().order_by('-date_created')[:5]
    context = {'rides_list': latest_rides, 'timezone': settings.TIME_ZONE}
    return render(request, 'rides-list.html', context)


def get_create_rate_form_class(request) -> DriverRateForm | ConsumerRateForm:
    if get_request_driver(request):
        return DriverRateForm
    elif get_request_consumer(request):
        return ConsumerRateForm
    raise ValueError(
        __name__,
        'User must be authenticated and signed as driver or consumer'
    )
    

def create_rate_view(request):
    form_class = get_create_rate_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            new_rate = form.save()
            ride = new_rate.ride
            return redirect(reverse('taxi:rides-detail', args=[ride.pk]))
    else:
        form = form_class(data=request.GET)
    return render(request,
        'create-rate.html',
        {
            'form': form
        }
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
    queryset = Address.objects.select_related('street', 'street__district', 'street__district__city').all()
    serializer_class = AddressSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'full_address']

    def get_queryset(self):
        addresses_list = cache.get('addresses_list')

        if not addresses_list:
            addresses_list = self.queryset
            cache.set('addresses_list', addresses_list, timeout=60 * 15)

        return addresses_list


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    pagination_class = LargeResultsSetPagination


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    pagination_class = LargeResultsSetPagination
    

    def get_queryset(self):
        available = self.kwargs.get('available')
        if available is None:
            return self.queryset
        return


class RideFilter(filters.FilterSet):
    min_created = filters.IsoDateTimeFilter(field_name='date_created', lookup_expr='gte')
    max_created = filters.IsoDateTimeFilter(field_name='date_created', lookup_expr='lte')
    min_ended = filters.IsoDateTimeFilter(field_name='date_ended', lookup_expr='gte')
    max_ended = filters.IsoDateTimeFilter(field_name='date_ended', lookup_expr='lte')
    
    class Meta:
        model = Ride
        fields = ['date_created', 'date_ended']


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all().order_by('-date_created')
    serializer_class = RideSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RideFilter

    def get_queryset(self):
        if 'available' in self.kwargs:
            return Ride.objects.available()
        return self.queryset

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
        if self.action in 'current accept complete_address add_address change_address'.split():
            return self.get_queryset().get(date_ended__isnull=True)
        return super().get_object()

    @action(methods=['GET'], detail=False)
    def available(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 

    @action(methods=['GET'], detail=False)
    def current(self, request, *args, **kwargs):
        user = get_request_user(request)
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        instance = get_object_or_404(Ride, Q(consumer=user.id) | Q(driver=user.id))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def accept(self, request, *args, **kwargs):
        driver = get_request_driver(request)
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
        driver = get_request_driver(request)

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

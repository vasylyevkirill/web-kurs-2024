from rest_framework.routers import SimpleRouter
from django.urls import path, include

from taxi.views import (
    CityViewSet,
    DistrictViewSet,
    StreetViewSet,
    AddressViewSet,
    CarViewSet,
    DriverViewSet,
    RideViewSet,
    available_rides_view,
    create_rate_view,
)

app_name = 'taxi'

router = SimpleRouter()
router.register(r'addresses', AddressViewSet, basename='addresses')
router.register(r'streets', StreetViewSet, basename='streets')
router.register(r'districts', DistrictViewSet, basename='districts')
router.register(r'cities', CityViewSet, basename='cities')
router.register(r'cars', CarViewSet, basename='cars')
router.register(r'drivers', DriverViewSet, basename='drivers')
router.register(r'rides', RideViewSet, basename='rides')


render_urlpatterns: list = [
    path(r'available/', available_rides_view, name='rides_available_render'),
    path(r'rate/create/', create_rate_view, name='create_ride_render'),
]

api_urlpatterns: list = [
    *router.urls,
]

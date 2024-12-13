from rest_framework.routers import SimpleRouter
from django.urls import path, include

from taxi.views import (
    CityViewSet,
    DistrictViewSet,
    StreetViewSet,
    AddressViewSet,
    CarViewSet,
    DriverViewSet,
)

app_name = 'taxi'

router = SimpleRouter()
router.register(r'addresses', AddressViewSet, basename='addresses')
router.register(r'streets', StreetViewSet, basename='streets')
router.register(r'districts', DistrictViewSet, basename='districts')
router.register(r'cities', CityViewSet, basename='cities')
router.register(r'cars', CarViewSet, basename='cars')
router.register(r'drivers', DriverViewSet, basename='drivers')

urlpatterns: list = [
    *router.urls,
]

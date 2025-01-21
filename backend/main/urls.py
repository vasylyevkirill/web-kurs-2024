from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from main.views import IndexView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from taxi.urls import api_urlpatterns as taxi_api_urlpatterns
from taxi.urls import render_urlpatterns as taxi_render_urlpatterns


urlpatterns = [ 
    path('', IndexView.as_view(), name='index'),
    path('render/', include((taxi_render_urlpatterns, 'taxi'), namespace='render')),
    path('api/', include((taxi_api_urlpatterns, 'taxi'), namespace='api')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

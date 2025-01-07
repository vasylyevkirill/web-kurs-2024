from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from main.views import IndexView

urlpatterns = [ 
    path('', IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('api/', include('taxi.urls', namespace='api')),
    path('accounts/', include('allauth.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

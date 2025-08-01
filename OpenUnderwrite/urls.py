from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('djadmin/', admin.site.urls),
    path('', include('open_underwrite.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

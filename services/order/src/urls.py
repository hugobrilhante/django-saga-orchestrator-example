from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path

from .core.urls import router

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'order/api/(?P<version>(v1|v2))/', include(router.urls)),
]

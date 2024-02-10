from django.contrib import admin
from django.urls import path, re_path, include

from .core.urls import router

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"order/api/(?P<version>(v1|v2))/", include(router.urls)),
]

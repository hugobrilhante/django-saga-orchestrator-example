from django.contrib import admin
from django.urls import path, re_path, include

from .core.urls import router

urlpatterns = [
    path("admin/", admin.site.urls),
]

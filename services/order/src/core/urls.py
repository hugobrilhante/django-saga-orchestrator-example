from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()

router.register(r"orders", OrderViewSet, basename="order")

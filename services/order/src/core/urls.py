from rest_framework.routers import DefaultRouter

from .views import OrderViewSet
from .views import TransactionViewSet

router = DefaultRouter()

router.register(r'orders', OrderViewSet, basename='order')
router.register(r'transactions', TransactionViewSet, basename='transaction')

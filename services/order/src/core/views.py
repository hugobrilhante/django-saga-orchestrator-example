from django.db import transaction
from rest_framework import viewsets

from .models import Order
from .orchestrator import orchestrator
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            order = serializer.save()
            data = {'amount': str(order.amount), 'items': serializer.data['items']}
            transaction_id = str(order.transaction_id)
            orchestrator.execute(
                action='create_reservation',
                data=data,
                transaction_id=transaction_id,
            )

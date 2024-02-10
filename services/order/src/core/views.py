from rest_framework import viewsets

from .models import Order
from .orchestrator import orchestrator
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        data = {'amount': str(order.amount), 'items': serializer.data['items']}
        transaction_id = str(order.transaction_id)
        orchestrator.perform(
            data=data,
            sender='order',
            service='stock',
            transaction_id=transaction_id,
        )

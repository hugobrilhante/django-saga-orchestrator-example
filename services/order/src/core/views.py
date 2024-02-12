import logging

from django_outbox_pattern.models import Published
from rest_framework import viewsets

from .models import Order
from .serializers import OrderSerializer

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        self._start_saga(serializer.data, instance.transaction_id)

    def _start_saga(self, data, transaction_id):
        logger.info(f'Starting saga with transaction_id: {transaction_id} and data: {data}')
        body = {'data': data, 'transaction_id': str(transaction_id), 'service': 'order', 'status': 'SUCCESS'}
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)

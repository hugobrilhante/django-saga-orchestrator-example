import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .models import Order
from .serializers import OrderSerializer

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
STOPPED = 'STOPPED'


def create_order(transaction_id, data):
    serializer = OrderSerializer(data={'transaction_id': transaction_id, **data})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info(f'Order created with transaction id: {transaction_id}')
    return SUCCESS


def cancel_order(transaction_id):
    order = Order.objects.get(transaction_id=transaction_id)
    order.status = Order.CANCELLED
    order.save()
    logger.info(f'Order canceled with transaction id: {transaction_id}')
    return STOPPED


def delivery_order(transaction_id):
    order = Order.objects.get(transaction_id=transaction_id)
    order.status = Order.DELIVERED
    order.save()
    logger.info(f'Order delivered with transaction id: {transaction_id}')
    return STOPPED


def handle_action(func, action, *args, **kwargs):
    try:
        status = func(*args, **kwargs)
    except Exception as exc:
        logger.exception(f'Error {action} order: {exc}')
        status = FAILED
    return status


def receiver(payload: Payload):
    action = payload.body['action']
    data = payload.body['data']
    transaction_id = payload.body['transaction_id']
    body = {
        'data': data,
        'service': 'order',
        'transaction_id': transaction_id,
    }
    with transaction.atomic():
        if action == 'create_order':
            status = handle_action(create_order, 'create', *(transaction_id, data))
        elif action == 'cancel_order':
            status = handle_action(cancel_order, 'cancel', *(transaction_id,))
        elif action == 'delivery_order':
            status = handle_action(delivery_order, 'delivery', *(transaction_id,))
        body.update({'status': status})
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
    payload.save()

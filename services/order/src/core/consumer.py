import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .models import Order
from .serializers import OrderSerializer

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
ROLL_BACK = 'ROLL_BACK'


def create_order(transaction_id, data):
    serializer = OrderSerializer(data={'transaction_id': transaction_id, **data})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info(f'Order created with transaction id: {transaction_id}')


def cancel_order(transaction_id):
    order = Order.objects.get(transaction_id=transaction_id)
    order.status = Order.CANCELLED
    order.save()
    logger.info(f'Order canceled with transaction id: {transaction_id}')


def delivery_order(transaction_id):
    order = Order.objects.get(transaction_id=transaction_id)
    order.status = Order.DELIVERED
    order.save()
    logger.info(f'Order delivered with transaction id: {transaction_id}')


def handle_action(func, action, status, *args, **kwargs):
    errors = None
    try:
        func(*args, **kwargs)
    except Exception as exc:
        logger.exception(f'Error {action} order: {exc}')
        errors = str(exc)
        status = FAILED
    return status, errors


def receiver(payload: Payload):
    status = payload.body['status']
    action = payload.body['action']
    data = payload.body['data']
    transaction_id = payload.body['transaction_id']
    body = {
        'data': data,
        'service': 'order',
        'transaction_id': transaction_id,
    }
    if status == FAILED:
        status = ROLL_BACK
    with transaction.atomic():
        errors = None
        if action == 'create_order':
            status, errors = handle_action(create_order, 'create', status, *(transaction_id, data))
        elif action == 'cancel_order':
            status, errors = handle_action(cancel_order, 'cancel', status, *(transaction_id,))
        elif action == 'delivery_order':
            status, errors = handle_action(delivery_order, 'delivery', status, *(transaction_id,))
        if errors is not None:
            body.update({'errors': errors})
        body.update({'status': status})
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
    payload.save()

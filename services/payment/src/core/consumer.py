import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .models import Payment
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)


def create_payment(transaction_id, data):
    serializer = PaymentSerializer(data={'transaction_id': transaction_id, **data})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info('Payment created with transaction id: %s', transaction_id)


def cancel_payment(transaction_id):
    payment = Payment.objects.get(transaction_id=transaction_id)
    payment.status = Payment.CANCELLED
    payment.save()
    logger.info('Payment canceled with transaction id: %s', transaction_id)


def confirm_payment(transaction_id):
    payment = Payment.objects.get(transaction_id=transaction_id)
    payment.status = Payment.CONFIRMED
    payment.save()
    logger.info('Payment confirmed with transaction id: %s', transaction_id)


def handle_action(func, action, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as exc:
        logger.exception(f'Error {action} reservation: {exc}')


def receiver(payload: Payload):
    action = payload.body['action']
    data = payload.body['data']
    sender = payload.body['sender']
    transaction_id = payload.body['transaction_id']
    body = {
        'action': action,
        'data': data,
        'sender': 'payment',
        'service': 'order',
        'transaction_id': transaction_id,
    }
    with transaction.atomic():
        if action and sender == 'stock':
            handle_action(create_payment, 'create', *(transaction_id, data))
        elif action and sender == 'order':
            handle_action(confirm_payment, 'confirm', *(transaction_id,))
        else:
            handle_action(cancel_payment, 'cancel', *(transaction_id,))
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
    payload.save()

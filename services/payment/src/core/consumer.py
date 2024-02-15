import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .models import Payment
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
ROLL_BACK = 'ROLL_BACK'


def create_payment(transaction_id, data):
    data.update(status=Payment.CONFIRMED)
    serializer = PaymentSerializer(data={'transaction_id': transaction_id, **data})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info(f'Payment created with transaction id: {transaction_id}')


def cancel_payment(transaction_id):
    payment = Payment.objects.get(transaction_id=transaction_id)
    payment.status = Payment.CANCELLED
    payment.save()
    logger.info(f'Payment canceled with transaction id: {transaction_id}')


def handle_action(func, action, status, *args, **kwargs):
    errors = None
    try:
        func(*args, **kwargs)
    except Exception as exc:
        logger.exception(f'Error {action} payment: {exc}')
        errors = str(exc)
        status = FAILED
    return status, errors


def receiver(payload: Payload):
    action = payload.body['action']
    data = payload.body['data']
    status = payload.body['status']
    transaction_id = payload.body['transaction_id']
    body = {
        'data': data,
        'service': 'payment',
        'transaction_id': transaction_id,
    }
    if status == FAILED:
        status = ROLL_BACK
    with transaction.atomic():
        errors = None
        if action == 'create_payment':
            status, errors = handle_action(create_payment, 'create', status, *(transaction_id, data))
        elif action == 'cancel_payment':
            status, errors = handle_action(cancel_payment, 'cancel', status, *(transaction_id,))
        if errors is not None:
            body.update({'errors': errors})
        body.update({'status': status})
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
    payload.save()

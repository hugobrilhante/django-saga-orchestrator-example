import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .models import Reservation
from .serializers import ReservationSerializer

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'


def create_reservation(transaction_id, data):
    serializer = ReservationSerializer(data={'transaction_id': transaction_id, **data})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info(f'Reservation created with transaction id: {transaction_id}')


def cancel_reservation(transaction_id):
    reservation = Reservation.objects.get(transaction_id=transaction_id)
    reservation.status = Reservation.CANCELLED
    reservation.save()
    logger.info(f'Reservation canceled with transaction id: {transaction_id}')


def confirm_reservation(transaction_id):
    reservation = Reservation.objects.get(transaction_id=transaction_id)
    reservation.status = Reservation.CONFIRMED
    reservation.save()
    logger.info(f'Reservation confirmed with transaction id: {transaction_id}')


def handle_action(func, action, status, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as exc:
        logger.exception(f'Error {action} reservation: {exc}')
        status = FAILED
    return status


def receiver(payload: Payload):
    action = payload.body['action']
    data = payload.body['data']
    status = payload.body['status']
    transaction_id = payload.body['transaction_id']
    body = {
        'data': data,
        'service': 'stock',
        'transaction_id': transaction_id,
    }
    with transaction.atomic():
        if action == 'create_reservation':
            status = handle_action(create_reservation, 'create', status, *(transaction_id, data))
        elif action == 'confirm_reservation':
            status = handle_action(confirm_reservation, 'confirm', status, *(transaction_id,))
        elif action == 'cancel_reservation':
            status = handle_action(cancel_reservation, 'cancel', status, *(transaction_id,))
        body.update({'status': status})
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
    payload.save()

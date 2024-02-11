import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .models import Reservation
from .serializers import ReservationSerializer

logger = logging.getLogger(__name__)


def create_reservation(transaction_id, data):
    serializer = ReservationSerializer(data={'transaction_id': transaction_id, **data})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info('Reservation created with transaction id: %s', transaction_id)


def cancel_reservation(transaction_id):
    reservation = Reservation.objects.get(transaction_id=transaction_id)
    reservation.status = Reservation.CANCELLED
    reservation.save()
    logger.info('Reservation canceled with transaction id: %s', transaction_id)


def confirm_reservation(transaction_id):
    reservation = Reservation.objects.get(transaction_id=transaction_id)
    reservation.status = Reservation.CONFIRMED
    reservation.save()
    logger.info('Reservation confirmed with transaction id: %s', transaction_id)


def handle_action(func, action, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as exc:
        logger.exception(f'Error {action} reservation: {exc}')


def receiver(payload: Payload):
    action = payload.body['action']
    data = payload.body['data']
    transaction_id = payload.body['transaction_id']
    body = {
        'action': 'create_payment',
        'data': data,
        'sender': 'stock',
        'transaction_id': transaction_id,
    }
    with transaction.atomic():
        if action == 'create_reservation':
            handle_action(create_reservation, 'create', *(transaction_id, data))
        elif action == 'confirm_reservation':
            handle_action(confirm_reservation, 'confirm', *(transaction_id,))
        elif action == 'cancel_reservation':
            handle_action(cancel_reservation, 'cancel', *(transaction_id,))
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
    payload.save()

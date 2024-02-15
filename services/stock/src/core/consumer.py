import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload
from rest_framework.exceptions import APIException

from .models import Reservation
from .serializers import ReservationSerializer

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
ROLL_BACK = 'ROLL_BACK'


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
    errors = None
    try:
        func(*args, **kwargs)
    except Exception as exc:
        if isinstance(exc, APIException):
            errors = exc.get_full_details()
        else:
            errors = str(exc)
        status = FAILED
        logger.exception(f'Error {action} order: {errors}')
    return status, errors


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
    if status == FAILED:
        status = ROLL_BACK
    with transaction.atomic():
        errors = None
        if action == 'create_reservation':
            status, errors = handle_action(create_reservation, 'create', status, *(transaction_id, data))
        elif action == 'confirm_reservation':
            status, errors = handle_action(confirm_reservation, 'confirm', status, *(transaction_id,))
        elif action == 'cancel_reservation':
            status, errors = handle_action(cancel_reservation, 'cancel', status, *(transaction_id,))
        if errors is not None:
            body.update({'errors': errors})
        body.update({'status': status})
        Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
    payload.save()

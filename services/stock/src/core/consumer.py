import logging

from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload
from rest_framework import serializers

from .models import Reservation
from .serializers import ReservationSerializer

logger = logging.getLogger(__name__)


def create_reservation(transaction_id, data):
    serializer = ReservationSerializer(data={"transaction_id": transaction_id, **data})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info("Reservation created with transaction id: %s", transaction_id)


def delete_reservation(transaction_id):
    reservation = Reservation.objects.get(transaction_id=transaction_id)
    reservation.delete()
    logger.info("Reservation deleted with transaction id: %s", transaction_id)


def receiver(payload: Payload):
    action = payload.body["action"]
    data = payload.body["data"]
    sender = payload.body["sender"]
    transaction_id = payload.body["transaction_id"]
    body = {
        "action": action,
        "data": data,
        "sender": "stock",
        "service": "payment",
        "transaction_id": transaction_id,
    }
    with transaction.atomic():
        error = None
        if action:
            try:
                create_reservation(transaction_id, data)
            except serializers.ValidationError as exc:
                error = str(exc)
        else:
            try:
                delete_reservation(transaction_id)
            except Reservation.DoesNotExist as exc:
                error = str(exc)
        if error is not None:
            body.update(action=False, service=sender)
        Published.objects.create(destination="/exchange/saga/orchestrator", body=body)
    payload.save()

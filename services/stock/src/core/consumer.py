from django.db import transaction
from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .models import Reservation
from .serializers import ReservationSerializer

def create_reservation(transaction_id, items):
    serializer = ReservationSerializer(data={"transaction_id": transaction_id, "items": items})
    serializer.is_valid(raise_exception=True)
    serializer.save()

def delete_reservation(transaction_id):
    reservation = Reservation.objects.get(id=transaction_id)
    reservation.delete()

def receiver(payload: Payload):
    action = payload.body['action']
    data = payload.body['data']
    sender = payload.body['sender']
    transaction_id = payload.body['transaction_id']
    body = {
        'action': action,
        'sender': 'stock',
        'transaction_id': transaction_id
    }
    with transaction.atomic():
        if action:
            create_reservation(transaction_id, data)
            body.update(service="payment")
        else:
            delete_reservation(transaction_id)
            body.update(action=False, service=sender)
        Published.objects.create(destination="/exchange/saga/orchestrator", body=body)
    payload.save()
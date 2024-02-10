import logging

from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

logger = logging.getLogger(__name__)


def handle_action(func, action, *args, **kwargs):
	try:
		func(*args, **kwargs)
	except Exception as exc:
		logger.exception(f'Error {action} reservation: {exc}')


def receiver(payload: Payload):
	action = payload.body['action']
	data = payload.body['data']
	_sender = payload.body['sender']
	transaction_id = payload.body['transaction_id']
	body = {
		'action': action,
		'data': data,
		'sender': 'payment',
		'service': 'delivery',
		'transaction_id': transaction_id,
	}
	Published.objects.create(destination='/exchange/saga/orchestrator', body=body)
	payload.save()

from typing import Any
from typing import Dict
from typing import Tuple

from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .interfaces import ActionAbstract
from .interfaces import PublisherAbstract


class Action(ActionAbstract):
    def __init__(self, action: str, destination: str):
        self.action = action
        self.destination = destination

    def execute(self, data: Any, transaction_id: str) -> Tuple[Dict[str, Any], str]:
        body = {
            'action': self.action,
            'data': data,
            'transaction_id': transaction_id,
        }
        return body, self.destination


class Publisher(PublisherAbstract):
    def send(self, destination, body):
        Published.objects.create(destination=destination, body=body)


class Orchestrator:
    def __init__(self, publisher: PublisherAbstract):
        self.publisher = publisher
        self.actions: Dict[str, Action] = {}

    def __call__(self, payload: Payload) -> None:
        self._receiver(payload.body)
        payload.save()

    def _sender(self, destination: str, body: dict) -> None:
        self.publisher.send(destination, body)

    def _receiver(self, body: dict) -> None:
        action = body.get('action')
        data = body.get('data')
        transaction_id = body.get('transaction_id')
        self.execute(action, data, transaction_id)

    def execute(self, action: str, data: dict, transaction_id: str) -> None:
        body, destination = self.actions[action].execute(data, transaction_id)
        self._sender(destination, body)

    def register_action(self, action: str, instance: Action) -> None:
        self.actions[action] = instance


class OrchestratorConfigurator:
    ORDER_DESTINATION = '/exchange/saga/order'
    STOCK_DESTINATION = '/exchange/saga/stock'
    PAYMENT_DESTINATION = '/exchange/saga/payment'
    DELIVERY_DESTINATION = '/exchange/saga/delivery'

    stages = {
        ORDER_DESTINATION: ['create_order', 'process_order', 'delivery_order'],
        STOCK_DESTINATION: ['create_reservation', 'confirm_reservation', 'cancel_reservation'],
        PAYMENT_DESTINATION: ['create_payment'],
        DELIVERY_DESTINATION: ['create_delivery'],
    }

    def __init__(self) -> None:
        self.orchestrator = Orchestrator(Publisher())
        for destination, actions in self.stages.items():
            for action in actions:
                self.orchestrator.register_action(action, Action(action, destination))

    def get_orchestrator(self) -> Orchestrator:
        return self.orchestrator


orchestrator = OrchestratorConfigurator().get_orchestrator()

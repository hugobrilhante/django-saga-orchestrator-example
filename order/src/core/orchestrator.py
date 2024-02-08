from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .interfaces import ActionAbstract
from .interfaces import CompensationAbstract
from .interfaces import PublisherAbstract


from typing import Any, Dict, Tuple


class OperationMixin:
    def __init__(self, destination: str, action: bool):
        self.destination = destination
        self.action = action

    def execute(
        self, data: Any, sender: str, transaction_id: int
    ) -> Tuple[Dict[str, Any], str]:
        body = {
            "action": self.action,
            "data": data,
            "sender": sender,
            "transaction_id": transaction_id,
        }
        return body, self.destination


class Action(ActionAbstract, OperationMixin):
    def __init__(self, destination: str):
        super().__init__(destination, action=True)

    def perform(
        self, data: Any, sender: str, transaction_id: int
    ) -> Tuple[Dict[str, Any], str]:
        return self.execute(data, sender, transaction_id)


class Compensation(CompensationAbstract, OperationMixin):
    def __init__(self, destination: str):
        super().__init__(destination, action=False)

    def compensate(
        self, data: Any, sender: str, transaction_id: int
    ) -> Tuple[Dict[str, Any], str]:
        return self.execute(data, sender, transaction_id)


class Publisher(PublisherAbstract):
    def send(self, destination, body):
        Published.objects.create(destination=destination, body=body)


class Orchestrator:
    def __init__(self, publisher: PublisherAbstract):
        self.publisher = publisher
        self.actions: Dict[str, Action] = {}
        self.compensations: Dict[str, Compensation] = {}

    def __call__(self, payload: Payload) -> None:
        self._receiver(payload.body)
        payload.save()

    def _sender(self, destination: str, body: dict) -> None:
        self.publisher.send(destination, body)

    def _receiver(self, body: dict) -> None:
        action = body.get("action")
        data = body.get("data")
        service = body.get("service")
        sender = body.get("sender")
        transaction_id = body.get("transaction_id")
        if action:
            self.perform(data, sender, service, transaction_id)
        else:
            self.compensate(data, sender, service, transaction_id)

    def perform(
        self, data: dict, sender: str, service: str, transaction_id: str
    ) -> None:
        body, destination = self.actions[service].perform(data, sender, transaction_id)
        self._sender(destination, body)

    def compensate(
        self, data: dict, sender: str, service: str, transaction_id: str
    ) -> None:
        body, destination = self.compensations[service].compensate(
            data, sender, transaction_id
        )
        self._sender(destination, body)

    def register_action(self, service: str, action: Action) -> None:
        self.actions[service] = action

    def register_compensation(self, service: str, compensation: Compensation) -> None:
        self.compensations[service] = compensation


# Orchestrator

orchestrator = Orchestrator(Publisher())

# Actions
reserve_product_action = Action("/exchange/saga/stock")
process_payment_action = Action("/exchange/saga/payment")
deliver_order_action = Action("/exchange/saga/delivery")
orchestrator.register_action("stock", reserve_product_action)
orchestrator.register_action("payment", process_payment_action)
orchestrator.register_action("delivery", deliver_order_action)

# Compensations
compensate_reserve_product = Compensation("/exchange/saga/stock")
compensate_process_payment = Compensation("/exchange/saga/payment")
compensate_deliver_order = Compensation("/exchange/saga/delivery")
orchestrator.register_compensation("stock", compensate_reserve_product)
orchestrator.register_compensation("payment", compensate_process_payment)
orchestrator.register_compensation("delivery", compensate_deliver_order)

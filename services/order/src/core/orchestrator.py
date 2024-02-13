import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .interfaces import ActionAbstract
from .interfaces import PublisherAbstract

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
STOPPED = 'STOPPED'


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
        self.actions: Dict[str, Action] = {}
        self.compensations: Dict[str, Action] = {}
        self.publisher = publisher
        self.steps: List[str] = []
        self.transactions_steps: Dict[str, List] = {}

    def __call__(self, payload: Payload) -> None:
        self._receiver(payload.body)
        payload.save()

    def _get_action(self, transaction_id: str) -> Action:
        action = self.transactions_steps[transaction_id].pop(0)
        logger.debug(f'Action in execution: {action}')
        return self.actions[action]

    def _get_compensate(self, service: str) -> Action:
        compensation = self.compensations[service]
        logger.debug(f'Compensation in execution: {compensation.action}')
        return compensation

    def _start_transaction(self, transaction_id: str) -> None:
        if transaction_id not in self.transactions_steps:
            self.transactions_steps[transaction_id] = self.steps.copy()
        logger.debug(f'Next steps: {self.transactions_steps[transaction_id]}')

    def _sender(self, destination: str, body: dict) -> None:
        self.publisher.send(destination, body)

    def _receiver(self, body: dict) -> None:
        data = body.get('data')
        status = body.get('status')
        service = body.get('service')
        transaction_id = body.get('transaction_id')
        self.execute(data, transaction_id, service, status)

    def execute(self, data: dict, transaction_id: str, service: str, status: str) -> None:
        self._start_transaction(transaction_id)
        if status == SUCCESS:
            body, destination = self._get_action(transaction_id).execute(data, transaction_id)
        elif status == FAILED:
            body, destination = self._get_compensate(service).execute(data, transaction_id)
        elif status == STOPPED:
            logger.info(f'Transaction concluded with transaction id: {transaction_id}')
        if status in [SUCCESS, FAILED]:
            logger.debug(f'Sending {body} to {destination} with status: {status}')
            body.update(status=status)
            self._sender(destination, body)

    def register_action(self, action: str, instance: Action) -> None:
        self.actions[action] = instance

    def register_compensation(self, service: str, instance: Action) -> None:
        self.compensations[service] = instance

    def register_steps(self, steps: List[str]) -> None:
        self.steps = steps


class OrchestratorConfigurator:
    saga = {
        'steps': ['create_reservation', 'create_payment', 'confirm_reservation', 'delivery_order'],
        'order': {
            'destination': '/exchange/saga/order',
            'actions': ['create_order', 'delivery_order'],
            'compensation': {'action': '', 'destination': ''},
        },
        'stock': {
            'destination': '/exchange/saga/stock',
            'actions': ['create_reservation', 'confirm_reservation'],
            'compensation': {'action': 'cancel_order', 'destination': '/exchange/saga/order'},
        },
        'payment': {
            'destination': '/exchange/saga/payment',
            'actions': ['create_payment'],
            'compensation': {'action': 'cancel_reservation', 'destination': '/exchange/saga/stock'},
        },
    }

    def __init__(self) -> None:
        steps = self.saga.pop('steps')
        self.orchestrator = Orchestrator(Publisher())
        self.orchestrator.register_steps(steps)
        for service, configs in self.saga.items():
            actions = configs['actions']
            destination = configs['destination']
            compensation = configs['compensation']
            for action in actions:
                self.orchestrator.register_action(action, Action(action, destination))
            action_compensation = compensation['action']
            destination_compensation = compensation['destination']
            self.orchestrator.register_compensation(service, Action(action_compensation, destination_compensation))

    def get_orchestrator(self) -> Orchestrator:
        return self.orchestrator


orchestrator = OrchestratorConfigurator().get_orchestrator()

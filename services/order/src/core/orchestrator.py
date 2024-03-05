import logging
from time import sleep
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from django_outbox_pattern.models import Published
from django_outbox_pattern.payloads import Payload

from .interfaces import ActionAbstract
from .interfaces import PublisherAbstract
from .models import Transaction

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
ROLL_BACK = 'ROLL_BACK'


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
        self.transactions: Dict[str, Transaction] = {}
        self.transactions_steps: Dict[str, List] = {}

    def __call__(self, payload: Payload) -> None:
        self._receiver(payload.body)
        payload.save()

    def _get_action(self, transaction_id: str) -> Action:
        try:
            action = self.transactions_steps[transaction_id].pop(0)
            logger.debug(f'Action in execution: {action}')
            return self.actions[action]
        except IndexError:
            return Action(action='stop_saga', destination='')

    def _get_compensate(self, service: str) -> Action:
        compensation = self.compensations[service]
        logger.debug(f'Compensation in execution: {compensation.action}')
        return compensation

    def _handle_success(self, data: dict, transaction_id: str, service: str, status: str) -> None:
        action = self._get_action(transaction_id)
        body, destination = action.execute(data, transaction_id)
        self._update_transaction(transaction_id, service, '#198754', 0.1)
        self._log_or_send(body, destination, transaction_id, status)

    def _handle_failed(self, data: dict, transaction_id: str, service: str, errors: str, status: str) -> None:
        compensate = self._get_compensate(service)
        body, destination = compensate.execute(data, transaction_id)
        logs = {service: f'Error on transaction id {transaction_id}: {errors}'}
        self._update_transaction(transaction_id, service, '#DC3545', 0.1, logs)
        self._log_or_send(body, destination, transaction_id, status)

    def _handle_roll_back(self, data: dict, transaction_id: str, service: str, status: str) -> None:
        compensate = self._get_compensate(service)
        body, destination = compensate.execute(data, transaction_id)
        self._update_transaction(transaction_id, service, '#FFC107', 0.1)
        self._log_or_send(body, destination, transaction_id, status)

    def _log_or_send(self, body: dict, destination: str, transaction_id: str, status: str) -> None:
        if not destination:
            logger.info(f'Transaction concluded with transaction id: {transaction_id}')
        else:
            logger.debug(f'Sending {body} to {destination} with status: {status}')
            body.update(status=status)
            self._sender(destination, body)

    def _start_transaction(self, transaction_id: str) -> None:
        if transaction_id not in self.transactions_steps:
            self.transactions[transaction_id] = Transaction.objects.create(transaction_id=transaction_id)
            self.transactions_steps[transaction_id] = self.steps.copy()
        logger.debug(f'Next steps: {self.transactions_steps[transaction_id]}')

    def _sender(self, destination: str, body: dict) -> None:
        self.publisher.send(destination, body)

    def _receiver(self, body: dict) -> None:
        data = body.get('data')
        errors = body.get('errors')
        status = body.get('status')
        service = body.get('service')
        transaction_id = body.get('transaction_id')
        self.execute(data, transaction_id, service, status, errors)

    def _update_transaction(
        self, transaction_id: str, service: str, color: str, delay: float = 0, logs: Optional[Dict] = None
    ) -> None:
        sleep(delay)
        transaction = self.transactions[transaction_id]
        for node in transaction.nodes:
            if node['data']['label'] == service:
                node['style']['background'] = color
        transaction.logs = logs
        transaction.save()

    def execute(self, data: dict, transaction_id: str, service: str, status: str, errors: str) -> None:
        self._start_transaction(transaction_id)
        if status == SUCCESS:
            self._handle_success(data, transaction_id, service, SUCCESS)
        elif status == FAILED:
            self._handle_failed(data, transaction_id, service, errors, FAILED)
        elif status == ROLL_BACK:
            self._handle_roll_back(data, transaction_id, service, ROLL_BACK)

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
            'compensation': {'action': None, 'destination': None},
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

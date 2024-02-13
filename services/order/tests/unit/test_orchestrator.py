from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

from django.test import TestCase

from src.core.orchestrator import FAILED
from src.core.orchestrator import STOPPED
from src.core.orchestrator import SUCCESS
from src.core.orchestrator import Action
from src.core.orchestrator import Orchestrator


class TestOrchestrator(TestCase):
    def setUp(self):
        publisher = MagicMock()
        self.orchestrator = Orchestrator(publisher)

    @patch('src.core.orchestrator.logger')
    def test_when_success(self, mock_logger):
        action_name = 'test_action'
        action = Action(action=action_name, destination='test_destination')
        action.execute = MagicMock(return_value=({}, 'test_destination'))
        self.orchestrator.register_steps([action_name])
        self.orchestrator.register_action(action_name, action)
        self.orchestrator.execute({}, 'transaction_id', 'test', SUCCESS)
        action.execute.assert_called_once_with({}, 'transaction_id')
        calls = [
            call("Next steps: ['test_action']"),
            call('Action in execution: test_action'),
            call(f'Sending {{}} to test_destination with status: {SUCCESS}'),
        ]
        mock_logger.debug.assert_has_calls(calls)

    @patch('src.core.orchestrator.logger')
    def test_when_failed(self, mock_logger):
        action_name = 'test_compensation'
        action = Action(action=action_name, destination='test_destination')
        action.execute = MagicMock(return_value=({}, 'test_destination'))
        self.orchestrator.register_steps([action_name])
        self.orchestrator.register_compensation('test_service', action)
        self.orchestrator.execute({}, 'transaction_id', 'test_service', FAILED)
        action.execute.assert_called_once_with({}, 'transaction_id')
        calls = [
            call("Next steps: ['test_compensation']"),
            call('Compensation in execution: test_compensation'),
            call(f'Sending {{}} to test_destination with status: {FAILED}'),
        ]
        mock_logger.debug.assert_has_calls(calls)

    @patch('src.core.orchestrator.logger')
    def test_when_stopped(self, mock_logger):
        action_name = 'test_action'
        action = Action(action=action_name, destination='test_destination')
        action.execute = MagicMock(return_value=({}, 'test_destination'))
        self.orchestrator.register_steps([action_name])
        self.orchestrator.register_action(action_name, action)
        self.orchestrator.execute({}, 'transaction_id', 'test', STOPPED)
        action.execute.assert_not_called()
        mock_logger.info.assert_called_once_with('Transaction concluded with transaction id: transaction_id')

    def test_receiver(self):
        payload = MagicMock()
        payload.body = {
            'data': [],
            'status': SUCCESS,
            'service': 'test_service',
            'transaction_id': 'test_transaction_id',
        }
        self.orchestrator.execute = MagicMock()
        self.orchestrator(payload)
        self.orchestrator.execute.assert_called_once_with([], 'test_transaction_id', 'test_service', SUCCESS)

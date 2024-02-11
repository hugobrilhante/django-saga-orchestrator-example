from unittest.mock import MagicMock

from django.test import TestCase

from src.core.orchestrator import Action
from src.core.orchestrator import Orchestrator


class TestOrchestrator(TestCase):
    def setUp(self):
        self.publisher_mock = MagicMock()
        self.orchestrator = Orchestrator(self.publisher_mock)
        self.payload = MagicMock()

    def test_perform_action(self):
        action = Action('test_action', 'destination_of_action')
        action.execute = MagicMock(return_value=({'key': 'value'}, 'destination_of_action'))
        self.orchestrator.register_action('test_action', action)

        self.payload.body = {
            'action': 'test_action',
            'data': {'key': 'value'},
            'service': 'test_service',
            'sender': 'test_sender',
            'transaction_id': '12345',
        }

        self.orchestrator(self.payload)

        action.execute.assert_called_once_with({'key': 'value'}, '12345')

        self.publisher_mock.send.assert_called_once_with('destination_of_action', {'key': 'value'})

from unittest.mock import MagicMock

from django.test import TestCase

from src.core.orchestrator import Action
from src.core.orchestrator import Compensation
from src.core.orchestrator import Orchestrator
from src.core.orchestrator import Payload


class TestOrchestrator(TestCase):
    def setUp(self):
        self.publisher_mock = MagicMock()
        self.orchestrator = Orchestrator(self.publisher_mock)
        self.payload = Payload(connection=MagicMock(), body=None, headers=None, message=MagicMock())

    def test_perform_action(self):
        action = Action('destination_of_action')
        action.perform = MagicMock(return_value=({'key': 'value'}, 'destination_of_action'))
        self.orchestrator.register_action('test_service', action)

        self.payload.body = {
            'action': 'test_action',
            'data': {'key': 'value'},
            'service': 'test_service',
            'sender': 'test_sender',
            'transaction_id': '12345',
        }

        self.orchestrator(self.payload)

        action.perform.assert_called_once_with({'key': 'value'}, 'test_sender', '12345')

        self.publisher_mock.send.assert_called_once_with('destination_of_action', {'key': 'value'})

    def test_compensate_action(self):
        compensation = Compensation('destination_of_compensation')
        compensation.compensate = MagicMock(return_value=({'key': 'value'}, 'destination_of_compensation'))
        self.orchestrator.register_compensation('test_service', compensation)

        self.payload.body = {
            'data': {'key': 'value'},
            'service': 'test_service',
            'sender': 'test_sender',
            'transaction_id': '12345',
        }

        self.orchestrator(self.payload)

        compensation.compensate.assert_called_once_with({'key': 'value'}, 'test_sender', '12345')

        self.publisher_mock.send.assert_called_once_with('destination_of_compensation', {'key': 'value'})

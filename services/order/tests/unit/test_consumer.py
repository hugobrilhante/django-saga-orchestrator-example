from unittest.mock import MagicMock
from unittest.mock import patch

from django.test import TestCase

from src.core.consumer import STOPPED
from src.core.consumer import SUCCESS
from src.core.consumer import cancel_order
from src.core.consumer import create_order
from src.core.consumer import delivery_order
from src.core.consumer import receiver


class TestConsumer(TestCase):
    @patch('src.core.consumer.Published.objects.create')
    @patch('src.core.consumer.handle_action', return_value=SUCCESS)
    def test_receiver_when_create_order(self, mock_handle_action, mock_published):
        payload = MagicMock()
        payload.body = {'action': 'create_order', 'data': [], 'transaction_id': 'test_transaction_id'}
        receiver(payload)
        mock_handle_action.assert_called_once_with(create_order, 'create', 'test_transaction_id', [])
        mock_published.assert_called_once_with(
            destination='/exchange/saga/orchestrator',
            body={'data': [], 'service': 'order', 'transaction_id': 'test_transaction_id', 'status': SUCCESS},
        )

    @patch('src.core.consumer.Published.objects.create')
    @patch('src.core.consumer.handle_action', return_value=STOPPED)
    def test_receiver_when_cancel_order(self, mock_handle_action, mock_published):
        payload = MagicMock()
        payload.body = {'action': 'cancel_order', 'data': [], 'transaction_id': 'test_transaction_id'}
        receiver(payload)
        mock_handle_action.assert_called_once_with(cancel_order, 'cancel', 'test_transaction_id')
        mock_published.assert_called_once_with(
            destination='/exchange/saga/orchestrator',
            body={'data': [], 'service': 'order', 'transaction_id': 'test_transaction_id', 'status': STOPPED},
        )

    @patch('src.core.consumer.Published.objects.create')
    @patch('src.core.consumer.handle_action', return_value=STOPPED)
    def test_receiver_when_delivery_order(self, mock_handle_action, mock_published):
        payload = MagicMock()
        payload.body = {'action': 'delivery_order', 'data': [], 'transaction_id': 'test_transaction_id'}
        receiver(payload)
        mock_handle_action.assert_called_once_with(delivery_order, 'delivery', 'test_transaction_id')
        mock_published.assert_called_once_with(
            destination='/exchange/saga/orchestrator',
            body={'data': [], 'service': 'order', 'transaction_id': 'test_transaction_id', 'status': STOPPED},
        )

    @patch('src.core.consumer.OrderSerializer')
    @patch('src.core.consumer.logger')
    def test_create_order(self, mock_logger, mock_order_serializer):
        create_order('test_transaction_id', {})
        mock_order_serializer.assert_called_once_with(data={'transaction_id': 'test_transaction_id'})
        mock_logger.info.assert_called_once_with('Order created with transaction id: test_transaction_id')

    @patch('src.core.consumer.Order.objects.get')
    @patch('src.core.consumer.logger')
    def test_cancel_order(self, mock_logger, mock_get):
        cancel_order('test_transaction_id')
        mock_get.assert_called_once_with(transaction_id='test_transaction_id')
        mock_logger.info.assert_called_once_with('Order canceled with transaction id: test_transaction_id')

    @patch('src.core.consumer.Order.objects.get')
    @patch('src.core.consumer.logger')
    def test_delivery_order(self, mock_logger, mock_get):
        delivery_order('test_transaction_id')
        mock_get.assert_called_once_with(transaction_id='test_transaction_id')
        mock_logger.info.assert_called_once_with('Order delivered with transaction id: test_transaction_id')

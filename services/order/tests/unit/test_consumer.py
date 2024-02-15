from unittest import mock

from django.test import TestCase

from src.core.consumer import cancel_order
from src.core.consumer import create_order
from src.core.consumer import delivery_order
from src.core.consumer import handle_action
from src.core.consumer import receiver


class TestConsumer(TestCase):
    def setUp(self):
        self.transaction_id = 'transaction_id'
        self.data = {'key': 'value'}
        self.payload = mock.MagicMock()
        self.payload.body = {
            'status': 'SUCCESS',
            'data': self.data,
            'sender': 'order',
            'transaction_id': self.transaction_id,
        }

    def test_create_order(self):
        self.payload.body['action'] = 'create_order'
        with mock.patch('src.core.consumer.OrderSerializer') as mock_serializer:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                create_order(self.transaction_id, self.data)
                mock_serializer.assert_called_once_with(data={'transaction_id': self.transaction_id, **self.data})
                mock_serializer.return_value.is_valid.assert_called_once()
                mock_serializer.return_value.save.assert_called_once()
                mock_logger.info.assert_called_once_with(f'Order created with transaction id: {self.transaction_id}')

    def test_cancel_order(self):
        self.payload.body['action'] = 'cancel_order'
        with mock.patch('src.core.consumer.Order.objects.get') as mock_get:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                mock_order = mock.Mock()
                mock_get.return_value = mock_order
                cancel_order(self.transaction_id)
                mock_order.save.assert_called_once()
                mock_logger.info.assert_called_once_with(f'Order canceled with transaction id: {self.transaction_id}')

    def test_delivery_order(self):
        self.payload.body['action'] = 'delivery_order'
        with mock.patch('src.core.consumer.Order.objects.get') as mock_get:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                mock_order = mock.Mock()
                mock_get.return_value = mock_order
                delivery_order(self.transaction_id)
                mock_order.save.assert_called_once()
                mock_logger.info.assert_called_once_with(f'Order delivered with transaction id: {self.transaction_id}')

    def test_handle_action(self):
        mock_func = mock.MagicMock()
        action = 'action'
        args = ('arg1',)
        kwargs = {'key': 'value'}
        with mock.patch('src.core.consumer.logger') as mock_logger:
            handle_action(mock_func, action, 'SUCCESS', *args, **kwargs)
            mock_func.assert_called_once_with(*args, **kwargs)
            mock_logger.exception.assert_not_called()

            # Test when an exception is raised
            exec_msg = 'Test Exception'
            mock_func.side_effect = Exception(exec_msg)
            handle_action(mock_func, action, 'SUCCESS', *args, **kwargs)
            mock_logger.exception.assert_called_once_with(f'Error {action} order: {exec_msg}')

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_create_order(self, mock_published_create):
        mock_create_order = mock.MagicMock()
        with mock.patch('src.core.consumer.create_order', mock_create_order):
            self.payload.body['action'] = 'create_order'
            receiver(self.payload)
            mock_create_order.assert_called_once_with(self.transaction_id, self.data)
            self.assertTrue(mock_published_create.called)

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_cancel_order(self, mock_published_create):
        mock_confirm_order = mock.MagicMock()
        with mock.patch('src.core.consumer.cancel_order', mock_confirm_order):
            self.payload.body['action'] = 'cancel_order'
            receiver(self.payload)
            mock_confirm_order.assert_called_once_with(self.transaction_id)
            self.assertTrue(mock_published_create.called)

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_delivery_order(self, mock_published_create):
        mock_delivery_order = mock.MagicMock()
        with mock.patch('src.core.consumer.delivery_order', mock_delivery_order):
            self.payload.body['action'] = 'delivery_order'
            receiver(self.payload)
            mock_delivery_order.assert_called_once_with(self.transaction_id)
            self.assertTrue(mock_published_create.called)

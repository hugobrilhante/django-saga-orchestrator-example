from unittest import mock

from django.test import TestCase

from src.core.consumer import cancel_payment
from src.core.consumer import create_payment
from src.core.consumer import handle_action
from src.core.consumer import receiver


class TestConsumer(TestCase):
    def setUp(self):
        self.transaction_id = 'transaction_id'
        self.data = {'key': 'value'}
        self.payload = mock.MagicMock()
        self.payload.body = {
            'data': self.data,
            'sender': 'order',
            'transaction_id': self.transaction_id,
        }

    def test_create_payment(self):
        self.payload.body['action'] = 'create_payment'
        with mock.patch('src.core.consumer.PaymentSerializer') as mock_serializer:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                create_payment(self.transaction_id, self.data)
                mock_serializer.assert_called_once_with(data={'transaction_id': self.transaction_id, **self.data})
                mock_serializer.return_value.is_valid.assert_called_once()
                mock_serializer.return_value.save.assert_called_once()
                mock_logger.info.assert_called_once_with(f'Payment created with transaction id: {self.transaction_id}')

    def test_cancel_payment(self):
        self.payload.body['action'] = 'cancel_payment'
        with mock.patch('src.core.consumer.Payment.objects.get') as mock_get:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                mock_payment = mock.Mock()
                mock_get.return_value = mock_payment
                cancel_payment(self.transaction_id)
                mock_payment.save.assert_called_once()
                mock_logger.info.assert_called_once_with(f'Payment canceled with transaction id: {self.transaction_id}')

    def test_handle_action(self):
        mock_func = mock.MagicMock()
        action = 'action'
        args = ('arg1',)
        kwargs = {'key': 'value'}
        with mock.patch('src.core.consumer.logger') as mock_logger:
            handle_action(mock_func, action, *args, **kwargs)
            mock_func.assert_called_once_with(*args, **kwargs)
            mock_logger.exception.assert_not_called()

            # Test when an exception is raised
            exec_msg = 'Test Exception'
            mock_func.side_effect = Exception(exec_msg)
            handle_action(mock_func, action, *args, **kwargs)
            mock_logger.exception.assert_called_once_with(f'Error {action} payment: {exec_msg}')

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_create_payment(self, mock_published_create):
        mock_create_payment = mock.MagicMock()
        with mock.patch('src.core.consumer.create_payment', mock_create_payment):
            self.payload.body['action'] = 'create_payment'
            receiver(self.payload)
            mock_create_payment.assert_called_once_with(self.transaction_id, self.data)
            self.assertTrue(mock_published_create.called)

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_cancel_payment(self, mock_published_create):
        mock_confirm_payment = mock.MagicMock()
        with mock.patch('src.core.consumer.cancel_payment', mock_confirm_payment):
            self.payload.body['action'] = 'cancel_payment'
            receiver(self.payload)
            mock_confirm_payment.assert_called_once_with(self.transaction_id)
            self.assertTrue(mock_published_create.called)

from unittest import mock

from django.test import TestCase

from src.core.consumer import cancel_reservation
from src.core.consumer import confirm_reservation
from src.core.consumer import create_reservation
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

    def test_create_reservation(self):
        self.payload.body['action'] = 'create_reservation'
        with mock.patch('src.core.consumer.ReservationSerializer') as mock_serializer:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                create_reservation(self.transaction_id, self.data)
                mock_serializer.assert_called_once_with(data={'transaction_id': self.transaction_id, **self.data})
                mock_serializer.return_value.is_valid.assert_called_once()
                mock_serializer.return_value.save.assert_called_once()
                mock_logger.info.assert_called_once_with(
                    f'Reservation created with transaction id: {self.transaction_id}'
                )

    def test_cancel_reservation(self):
        self.payload.body['action'] = 'cancel_reservation'
        with mock.patch('src.core.consumer.Reservation.objects.get') as mock_get:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                mock_reservation = mock.Mock()
                mock_get.return_value = mock_reservation
                cancel_reservation(self.transaction_id)
                mock_reservation.save.assert_called_once()
                mock_logger.info.assert_called_once_with(
                    f'Reservation canceled with transaction id: {self.transaction_id}'
                )

    def test_confirm_reservation(self):
        self.payload.body['action'] = 'confirm_reservation'
        with mock.patch('src.core.consumer.Reservation.objects.get') as mock_get:
            with mock.patch('src.core.consumer.logger') as mock_logger:
                mock_reservation = mock.Mock()
                mock_get.return_value = mock_reservation
                confirm_reservation(self.transaction_id)
                mock_reservation.save.assert_called_once()
                mock_logger.info.assert_called_once_with(
                    f'Reservation confirmed with transaction id: {self.transaction_id}'
                )

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
            mock_logger.exception.assert_called_once_with(f'Error {action} reservation: {exec_msg}')

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_create_reservation(self, mock_published_create):
        mock_create_reservation = mock.MagicMock()
        with mock.patch('src.core.consumer.create_reservation', mock_create_reservation):
            self.payload.body['action'] = 'create_reservation'
            receiver(self.payload)
            mock_create_reservation.assert_called_once_with(self.transaction_id, self.data)
            self.assertTrue(mock_published_create.called)

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_cancel_reservation(self, mock_published_create):
        mock_confirm_reservation = mock.MagicMock()
        with mock.patch('src.core.consumer.cancel_reservation', mock_confirm_reservation):
            self.payload.body['action'] = 'cancel_reservation'
            receiver(self.payload)
            mock_confirm_reservation.assert_called_once_with(self.transaction_id)
            self.assertTrue(mock_published_create.called)

    @mock.patch('src.core.consumer.Published.objects.create')
    def test_receiver_confirm_reservation(self, mock_published_create):
        mock_cancel_reservation = mock.MagicMock()
        with mock.patch('src.core.consumer.confirm_reservation', mock_cancel_reservation):
            self.payload.body['action'] = 'confirm_reservation'
            receiver(self.payload)
            mock_cancel_reservation.assert_called_once_with(self.transaction_id)
            self.assertTrue(mock_published_create.called)

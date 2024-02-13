from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from src.core.models import Order
from src.core.models import OrderItem


class OrderIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_order_with_items(self):
        order_data = {
            'customer_id': 123,
            'items': [
                {'product': 1, 'quantity': 2, 'price': 10.0},
                {'product': 2, 'quantity': 1, 'price': 20.0},
            ],
        }

        with patch('src.core.views.Published.objects.create') as mock_create:
            response = self.client.post('/order/api/v1/orders/', data=order_data, format='json')

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()

        self.assertEqual(OrderItem.objects.count(), 2)
        order_items = OrderItem.objects.filter(order=order)

        self.assertEqual(order_items[0].product, '1')
        self.assertEqual(order_items[0].quantity, 2)
        self.assertEqual(order_items[0].price, 10.0)
        self.assertEqual(order_items[1].product, '2')
        self.assertEqual(order_items[1].quantity, 1)
        self.assertEqual(order_items[1].price, 20.0)

        body = {
            'data': response.data,
            'transaction_id': str(order.transaction_id),
            'service': 'order',
            'status': 'SUCCESS',
        }
        mock_create.assert_called_once_with(destination='/exchange/saga/orchestrator', body=body)

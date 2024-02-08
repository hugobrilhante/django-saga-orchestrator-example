from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from src.core.models import Order, Product, OrderItem


class OrderIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_order_with_items(self):
        product1 = Product.objects.create(
            name="Product 1", description="Description 1", price=10.0
        )
        product2 = Product.objects.create(
            name="Product 2", description="Description 2", price=20.0
        )

        order_data = {
            "customer_id": 123,
            "items": [
                {"product": product1.id, "quantity": 2, "price": 10.0},
                {"product": product2.id, "quantity": 1, "price": 20.0},
            ],
        }

        with patch("src.core.views.orchestrator.perform") as mock_perform:
            response = self.client.post(
                "/order/api/v1/orders/", data=order_data, format="json"
            )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()

        self.assertEqual(OrderItem.objects.count(), 2)
        order_items = OrderItem.objects.filter(order=order)

        self.assertEqual(order_items[0].product, product1)
        self.assertEqual(order_items[0].quantity, 2)
        self.assertEqual(order_items[0].price, 10.0)
        self.assertEqual(order_items[1].product, product2)
        self.assertEqual(order_items[1].quantity, 1)
        self.assertEqual(order_items[1].price, 20.0)

        mock_perform.assert_called_once_with(
            data=response.data["items"],
            sender="order",
            service="stock",
            transaction_id=str(order.transaction_id),
        )

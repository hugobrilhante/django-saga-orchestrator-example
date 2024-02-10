from rest_framework import serializers

from .models import Order
from .models import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderItem
		fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True)

	class Meta:
		model = Order
		fields = [
			'id',
			'customer_id',
			'status',
			'transaction_id',
			'created',
			'modified',
			'items',
		]

	def validate_items(self, value):
		if not value:
			raise serializers.ValidationError('Must have at least 1 item')
		return value

	def create(self, validated_data):
		items = validated_data.pop('items')
		order = Order.objects.create(**validated_data)
		for item in items:
			OrderItem.objects.create(order=order, **item)
		return order

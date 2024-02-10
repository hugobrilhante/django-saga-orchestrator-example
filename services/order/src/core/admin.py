from django.contrib import admin

from .models import Order
from .models import OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = [
		'id',
		'customer_id',
		'created',
		'modified',
		'status',
		'transaction_id',
	]
	list_filter = ['status']
	search_fields = ['id', 'customer_id']
	readonly_fields = ['created', 'modified', 'transaction_id']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ['id', 'order', 'product', 'quantity', 'price']
	list_filter = ['order__status']
	search_fields = ['order__id', 'product']

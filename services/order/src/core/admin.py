from django.contrib import admin

from .models import Order
from .models import OrderItem
from .models import Transaction


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'price']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'customer_id', 'status', 'created', 'modified']
    list_filter = ['status']
    search_fields = ['id', 'customer_id']
    readonly_fields = ['created', 'modified', 'transaction_id']
    inlines = [OrderItemInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'nodes', 'logs']
    search_fields = ['transaction_id']
    list_filter = ['transaction_id']

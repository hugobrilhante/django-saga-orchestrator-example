from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'status', 'created', 'modified')
    list_filter = ('status', 'created', 'modified')
    search_fields = ('transaction_id',)
    readonly_fields = ('transaction_id', 'created', 'modified')

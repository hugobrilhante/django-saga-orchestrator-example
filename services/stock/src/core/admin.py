from django.contrib import admin

from .models import Product
from .models import Reservation
from .models import ReservationItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'price']
    search_fields = ['name']


class ReservationItemInline(admin.TabularInline):
    model = ReservationItem
    extra = 0


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'status', 'created', 'modified']
    search_fields = ['transaction_id']
    readonly_fields = ['transaction_id', 'created', 'modified']
    inlines = [ReservationItemInline]

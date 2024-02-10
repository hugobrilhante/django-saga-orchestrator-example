from django.contrib import admin

from .models import Product
from .models import Reservation
from .models import ReservationItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'description', 'price']
	search_fields = ['name']


class ReservationItemInline(admin.TabularInline):  # ou admin.StackedInline
	model = ReservationItem
	extra = 0


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
	list_display = ['id', 'transaction_id', 'created']
	search_fields = ['transaction_id']
	inlines = [ReservationItemInline]


@admin.register(ReservationItem)
class ReservationItemAdmin(admin.ModelAdmin):
	list_display = ['id', 'product', 'reservation', 'quantity', 'price']
	list_filter = ['product']
	search_fields = ['product__name', 'reservation__transaction_id']

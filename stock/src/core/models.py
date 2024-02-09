from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    customer_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100)

    def __str__(self):
        return f"Reservation ID: {self.transaction_id}"

    def validate_quantity_available(self):
        for item in self.items.all():
            if item.quantity > item.product.quantity:
                raise ValidationError(
                    "There is not enough quantity of this product available."
                )

    def save(self, *args, **kwargs):
        self.validate_quantity_available()
        super().save(*args, **kwargs)


class ReservationItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reservation = models.ForeignKey(
        Reservation, related_name="items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Reservation #{self.reservation.id})"

from django.db import models


class Payment(models.Model):
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    STATUS_CHOICES = (
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100)

    def __str__(self):
        return f'Payment ID: {self.transaction_id}'

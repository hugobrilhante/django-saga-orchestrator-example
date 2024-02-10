# Generated by Django 5.0.2 on 2024-02-10 19:10

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    'status',
                    models.CharField(
                        choices=[('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')],
                        default='pending',
                        max_length=20,
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('transaction_id', models.CharField(max_length=100)),
            ],
        ),
    ]

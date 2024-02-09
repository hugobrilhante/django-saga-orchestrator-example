from rest_framework import serializers
from .models import Reservation, ReservationItem


class ReservationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationItem
        fields = ["product", "quantity", "price"]


class ReservationSerializer(serializers.ModelSerializer):
    items = ReservationItemSerializer(many=True)

    class Meta:
        model = Reservation
        fields = ["customer_id", "transaction_id", "items"]

    def create(self, validated_data):
        items = validated_data.pop("items")
        reservation = Reservation.objects.create(**validated_data)
        for item in items:
            ReservationItem.objects.create(reservation=reservation, **item)
        return reservation

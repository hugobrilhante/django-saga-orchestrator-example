from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def validate_amount(self, value):
        if value > 5000:
            raise serializers.ValidationError('Amount must be less than or equal to 5000.')
        return value

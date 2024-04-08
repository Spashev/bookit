from rest_framework import serializers
from product.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            'id',
            'start_date',
            'end_date',
            'product'
        )


class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            'id',
            'start_date',
            'end_date',
            'product',
            'user_name',
            'phone'
        )

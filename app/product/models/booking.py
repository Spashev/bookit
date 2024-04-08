from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from product.models.products import Product


class Booking(models.Model):
    start_date = models.DateField(verbose_name='Дата заезда')
    end_date = models.DateField(verbose_name='Дата выезда')
    product = models.ForeignKey(to=Product, related_name='booking', on_delete=models.CASCADE, default=1)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

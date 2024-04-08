# Generated by Django 5.0.3 on 2024-04-05 11:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0016_alter_booking_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='product_pro_name_b60cd1_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['price_per_night'], name='product_pro_price_p_19e502_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['rooms_qty'], name='product_pro_rooms_q_8d8793_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['guest_qty'], name='product_pro_guest_q_f9444d_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['type'], name='product_pro_type_id_9633ca_idx'),
        ),
    ]
# Generated by Django 5.0.3 on 2024-03-23 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_booking_phone_booking_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='best_product',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='promotion',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.0.3 on 2024-03-29 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_product_best_product_product_promotion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
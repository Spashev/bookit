# Generated by Django 5.0.3 on 2024-04-03 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_user_first_name_alter_user_last_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='middle_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Отчество'),
        ),
    ]
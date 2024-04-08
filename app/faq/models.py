from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from helpers.models import TimestampMixin


class HelpCenter(TimestampMixin, models.Model):
    email = models.CharField(max_length=255)
    phone_number = PhoneNumberField(null=True, blank=True)
    text = models.TextField()
    is_approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'help_centers'


class Faq(TimestampMixin, models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()

    class Meta:
        db_table = 'faq'

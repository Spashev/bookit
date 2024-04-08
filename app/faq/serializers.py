from rest_framework import serializers
from django.core.validators import EmailValidator
from faq.models import HelpCenter, Faq
from django.conf import settings
from product.tasks import send_email_message


class HelpCenterSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=2500)
    phone_number = serializers.CharField(min_length=10, max_length=22)
    email = serializers.CharField(max_length=255, validators=[EmailValidator()])

    class Meta:
        model = HelpCenter
        fields = (
            'text',
            'phone_number',
            'email',
        )

    def create(self, validated_data):
        instance = super().create(validated_data)

        message = f"A new help center entry has been created. ID: {instance.id}, email: {instance.email}."
        send_email_message.delay(
            'New Help Center Entry',
            message,
            settings.EMAIL_HOST_USER,
            [settings.SUPPORT_EMAIL]
        )

        return instance


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = '__all__'

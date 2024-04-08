from django.conf import settings
from rest_framework import serializers

from account.models import User
from product.models import Image
from helpers.mixins import ImageMinioCorrectPathMixin


class ShareItemSerializer(serializers.Serializer):
    url = serializers.URLField()
    name = serializers.CharField()
    image = serializers.CharField()


class UserSerializer(serializers.ModelSerializer, ImageMinioCorrectPathMixin):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'avatar'
        )
        read_only_fields = ['id']

    def get_avatar(self, obj):
        if isinstance(obj, dict):
            return self._get_image_url(obj.get('avatar'))
        return self._get_image_url(obj.avatar)


class ImageSerializer(serializers.ModelSerializer, ImageMinioCorrectPathMixin):
    original = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = (
            'id',
            'original',
            'thumbnail',
            'width',
            'height',
            'mimetype',
            'is_label'
        )

    def get_original(self, obj):
        return self._get_image_url(obj.original)

    def get_thumbnail(self, obj):
        return self._get_image_url(obj.thumbnail)


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class PhoneSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'phone',
        )


class EmailSerializer(serializers.ModelSerializer):
    email = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'email',
        )


class IconSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return self._get_image_url(obj.icon)

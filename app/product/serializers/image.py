import os
from rest_framework import serializers

from product.models import Image
from helpers.validator import MAX_FILE_SIZE


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class UploadFilesSerializer(serializers.ModelSerializer):
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=MAX_FILE_SIZE, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    class Meta:
        model = Image
        fields = (
            'id',
            'uploaded_files',
        )
        read_only_fields = (
            'id',
        )


class ImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = (
            'id',
            'is_label',
            'original',
            'thumbnail',
            'product',
        )

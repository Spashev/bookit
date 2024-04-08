import uuid
import os
from PIL import Image, ImageOps
from io import BytesIO
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import ImageField
from helpers.logger import log_exception
from django.core.files.storage import default_storage

from account.authentication import JWTAuthentication


class UserQuerySetMixin:
    user_filed = 'user'
    allow_staff_view = False

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        lookup_data = {self.user_filed: user}
        qs = super().get_queryset(*args, **kwargs)
        if not self.allow_staff_view and not user.is_staff:
            return qs
        return qs.filter(**lookup_data)


class ResizeImageMixin:

    def resize(self, image_field: ImageField, quality: int = 90, resize: float = 1):
        try:
            im = Image.open(image_field)
            mime_type = 'webp'
            output = BytesIO()
            width, height = im.size

            new_width, new_height = int(width * resize), int(height * resize)
            im = im.resize((new_width, new_height), Image.LANCZOS)

            im.save(output, format=mime_type, quality=quality, optimize=True)
            content_file = ContentFile(output.getvalue())
            file = File(content_file)

            random_name = f'{uuid.uuid4()}.{mime_type}'
            image_field.save(random_name, file, save=False)

            return width, height, mime_type
        except Exception as e:
            log_exception(e, f'Failed to resize image {str(e)}')


class ProductContextSerializerMixins:
    def get_serializer_context(self):
        jwt = JWTAuthentication()
        user = jwt.authenticate(self.request)
        return {'user_id': user[0].id} if user is not None else None


class ImageMinioCorrectPathMixin:
    def _get_image_url(self, image_field):
        if not image_field:
            return None
        return f'{settings.AWS_S3_IMAGE_DOMAIN}/{image_field.name}'

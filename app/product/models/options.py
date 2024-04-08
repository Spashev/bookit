from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.dispatch import receiver
from PIL import Image as PILImage

from helpers.models import TimestampMixin, CharNameModel
from helpers.mixins import ResizeImageMixin
from helpers.logger import log_exception
from helpers.utils import delete_file
from helpers.constants import MB_SIZE, ORIGINAL_QUALITY, THUMBNAIL_QUALITY


class Category(CharNameModel, models.Model):
    is_active = models.BooleanField(verbose_name=_('Активный'), default=True)
    icon = models.FileField(verbose_name=_('Иконки'), upload_to='icons/categories', null=True, blank=True)

    class Meta:
        db_table = 'categories'
        ordering = ("-pk",)
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name


class Convenience(CharNameModel, models.Model):
    is_active = models.BooleanField(verbose_name=_('Активный'), default=True)
    icon = models.FileField(verbose_name=_('Иконки'), upload_to='icons/conveniences', null=True, blank=True)

    class Meta:
        db_table = 'conveniences'
        ordering = ("-pk",)
        verbose_name = _('Условия')
        verbose_name_plural = _('Условии')

    def __str__(self):
        return self.name


class Type(CharNameModel, TimestampMixin, models.Model):
    icon = models.FileField(verbose_name=_('Иконки'), upload_to='icons/conveniences', null=True, blank=True)

    class Meta:
        db_table = 'types'
        ordering = ("-created_at",)
        verbose_name = _('Тип построении домов')
        verbose_name_plural = _('Тип построении домов')

    def __str__(self):
        return self.name


class Image(models.Model, ResizeImageMixin):
    original = models.ImageField(verbose_name=_('Оригинальная картина'), upload_to='images/original/%Y/%m/%d')
    thumbnail = models.ImageField(verbose_name=_('Thumbnail картина'), upload_to='images/thumbnail/%Y/%m/%d', null=True)
    width = models.IntegerField(verbose_name=_('Width'), blank=True, null=True)
    height = models.IntegerField(verbose_name=_('Height'), blank=True, null=True)
    mimetype = models.CharField(max_length=300, default=None, blank=True, null=True)
    size = models.IntegerField(default=None, blank=True, null=True)
    product = models.ForeignKey('product.Product', verbose_name=_('Продукт'), related_name='images',
                                on_delete=models.CASCADE, null=True, blank=True)
    is_label = models.BooleanField(default=False)

    class Meta:
        db_table = 'images'
        ordering = ("-pk",)
        verbose_name = _('Картинка продукта')
        verbose_name_plural = _('Картинки продуктов')

    def clean_original(self):
        image = self.cleaned_data.get('original', False)
        if image:
            if image.size > 4 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 4mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

    def image_tag(self):
        if self.original.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.original.url))
        else:
            return ""

    def save(self, *args, **kwargs):
        if self.pk is None:
            original_quality, thumbnail_quality = self.get_qualities()

            original_width, original_height, mime_type = self.resize(
                image_field=self.original,
                quality=original_quality,
                resize=0.90
            )
            self.resize(
                image_field=self.thumbnail,
                quality=thumbnail_quality,
                resize=0.55
            )

            self.width = original_width
            self.height = original_height
            self.mimetype = mime_type
        super().save(*args, **kwargs)

    def get_qualities(self):
        original_quality, thumbnail_quality = ORIGINAL_QUALITY, THUMBNAIL_QUALITY
        original_image_size = self.original.size

        if original_image_size >= 2 * MB_SIZE:
            original_quality -= 45
            thumbnail_quality -= 25
        elif original_image_size >= MB_SIZE:
            original_quality -= 35
            thumbnail_quality -= 20
        elif original_image_size >= 700000:
            original_quality -= 25
            thumbnail_quality -= 15
        elif original_image_size >= 400000:
            original_quality -= 15
            thumbnail_quality -= 10
        elif original_image_size >= 200000:
            original_quality -= 10
            thumbnail_quality -= 6
        elif original_image_size >= 100000:
            original_quality -= 5
            thumbnail_quality -= 4
        original_quality = min(max(original_quality, 0), 100)
        thumbnail_quality = min(max(thumbnail_quality, 0), 100)

        return original_quality, thumbnail_quality

    def delete(self, *args, **kwargs):
        self.__delete_image_from_minio()
        super().delete(*args, **kwargs)

    def __delete_image_from_minio(self):
        if self.original:
            original_image_name = self.original.name
            try:
                delete_file(original_image_name)
            except Exception as e:
                log_exception(e, "Error deleting original image from MinIO")
        if self.thumbnail:
            thumbnail_image_name = self.thumbnail.name
            try:
                delete_file(thumbnail_image_name)
            except Exception as e:
                log_exception(e, "Error deleting thumbnail image from MinIO")

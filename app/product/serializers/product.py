from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Prefetch, OuterRef
from rest_framework import serializers

from product.models import Product, Category, Convenience, Type, Like, Favorites
from product.serializers import booking, comment
from product.tasks import send_email_message
from django.db.models import Q

from helpers.serializers import ImageSerializer, UserSerializer, ShareItemSerializer, IconSerializer
from helpers.logger import log_exception
from helpers.mixins import ImageMinioCorrectPathMixin
from product.services import get_product_bookings, sort_products_images


class CategorySerializer(IconSerializer, ImageMinioCorrectPathMixin):
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'icon'
        )


class ConvenienceSerializer(IconSerializer, ImageMinioCorrectPathMixin):
    class Meta:
        model = Convenience
        fields = (
            'id',
            'name',
            'icon'
        )


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class ProductRetrieveSerializer(serializers.ModelSerializer):
    convenience = ConvenienceSerializer(many=True, read_only=True)
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    bookings = booking.BookingSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    owner = UserSerializer()
    is_favorite = serializers.SerializerMethodField()
    is_new = serializers.BooleanField(default=False)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price_per_night',
            'price_per_week',
            'price_per_month',
            'owner',
            'rooms_qty',
            'guest_qty',
            'bed_qty',
            'bedroom_qty',
            'toilet_qty',
            'bath_qty',
            'description',
            'city',
            'address',
            'convenience',
            'type',
            'images',
            'lat',
            'lng',
            'bookings',
            'comments',
            'like_count',
            'rating',
            'is_favorite',
            'is_new',
            'best_product',
            'promotion'
        )

    def get_comments(self, obj):
        comments = obj.product_comments.filter(is_active=True)[:6]
        serializer = comment.CommentListSerializer(comments, many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        filtered_bookings = get_product_bookings(instance)
        serialized_bookings = booking.BookingSerializer(filtered_bookings, many=True).data
        representation['bookings'] = serialized_bookings
        representation['images'] = sort_products_images(representation.pop('images'))

        return representation

    def get_is_favorite(self, obj):
        return hasattr(obj, 'is_favorite') and obj.is_favorite


class ProductListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    owner = UserSerializer()
    is_favorite = serializers.SerializerMethodField()
    is_new = serializers.BooleanField(default=False)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price_per_night',
            'owner',
            'city',
            'address',
            'images',
            'is_favorite',
            'rating',
            'like_count',
            'is_new',
            'best_product',
            'promotion',
            'is_active'
        )

    def get_is_favorite(self, obj):
        return hasattr(obj, 'is_favorite') and obj.is_favorite

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = sort_products_images(representation.pop('images'))

        return representation


class ProductCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    rooms_qty = serializers.IntegerField(max_value=9999)
    guest_qty = serializers.IntegerField(max_value=9999)
    bed_qty = serializers.IntegerField(max_value=9999)
    bedroom_qty = serializers.IntegerField(max_value=9999)
    toilet_qty = serializers.IntegerField(max_value=9999)
    bath_qty = serializers.IntegerField(max_value=9999)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price_per_night',
            'price_per_week',
            'price_per_month',
            'owner',
            'rooms_qty',
            'guest_qty',
            'guests_with_babies',
            'guests_with_pets',
            'bed_qty',
            'bedroom_qty',
            'toilet_qty',
            'bath_qty',
            'description',
            'category',
            'city',
            'address',
            'convenience',
            'type',
            'lat',
            'lng'
        )

        read_only_fields = (
            'id',
        )

    def create(self, validated_data):
        try:
            category = validated_data.pop('category')
            convenience = validated_data.pop('convenience')
            product = Product.objects.create(**validated_data)
            product.category.set(category)
            product.convenience.set(convenience)

            message = f"A new product entry has been created, plz verify it. ID: {product.id}, name: {product.name}."
            send_email_message.delay(
                'New Product created.',
                message,
                settings.EMAIL_HOST_USER,
                [settings.SUPPORT_EMAIL]
            )

            return product
        except Exception as e:
            log_exception(e, f'Create product error {str(e)}')


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'name',
            'price_per_night',
            'price_per_week',
            'price_per_month',
            'rooms_qty',
            'guest_qty',
            'guests_with_babies',
            'guests_with_pets',
            'bed_qty',
            'bedroom_qty',
            'toilet_qty',
            'bath_qty',
            'description',
            'category',
            'city',
            'address',
            'convenience',
            'type',
            'lat',
            'lng'
        )

    def update(self, instance, validated_data):
        instance.is_active = False

        message = f"A product was updated, plz verify it. ID: {instance.id}, name: {instance.name}."
        send_email_message.delay(
            'The Product updated.',
            message,
            settings.EMAIL_HOST_USER,
            [settings.SUPPORT_EMAIL]
        )

        return super().update(instance, validated_data)


class ProductPreviewSerializer(serializers.ModelSerializer):
    convenience = ConvenienceSerializer(many=True, read_only=True)
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price_per_night',
            'price_per_week',
            'price_per_month',
            'rooms_qty',
            'guest_qty',
            'bed_qty',
            'bedroom_qty',
            'toilet_qty',
            'bath_qty',
            'description',
            'city',
            'address',
            'convenience',
            'type',
            'images',
            'lat',
            'lng',
            'rating',
            'is_active',
            'guests_with_babies',
            'guests_with_pets',
            'promotion',
            'best_product'
        )


class ProductLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = (
            'user',
        )

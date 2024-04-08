import random
from datetime import datetime, timedelta
from rest_framework import viewsets, mixins, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from django.db.models import Q, Exists, OuterRef, Prefetch, Case, When, Value, BooleanField

from helpers.logger import log_exception
from product.serializers import (
    ProductListSerializer,
    ProductCreateSerializer,
    BookingSerializer,
    ProductLikeSerializer,
    ProductRetrieveSerializer,
    UploadFilesSerializer,
    CategorySerializer,
    CommentSerializer,
    TypeSerializer,
    ConvenienceSerializer,
    ImageSerializer,
    ProductUpdateSerializer,
    ProductPreviewSerializer,
    CreateBookingSerializer,
)
from product.models import Product, Booking, Image, Category, Comment, Favorites, Type, Convenience
from product.filters import BookingFilterSet
from product.permissions import ProductPermissions, CommentPermissions, ProductPreviewPermissions
from helpers.mixins import ProductContextSerializerMixins
from helpers.services import update_instance
from product.services import (
    like_or_dislike,
    save_image,
    get_product_by_id_user_id,
    paginate_queryset,
    get_product_queryset,
    get_query_filter,
    get_favorite_products_data,
    get_favorite_products,
    get_product_bookings,
    get_user_products,
)
from product.openapi import manual_parameters, limit, offset, start_date, end_date, active


class ProductViewSet(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductPermissions)
    queryset = Product.with_related.all()

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == 'create':
            serializer = ProductCreateSerializer
        elif self.action == 'like':
            serializer = ProductLikeSerializer
        elif self.action == 'save_image':
            serializer = UploadFilesSerializer
        elif self.action == 'get_user_products':
            serializer = UploadFilesSerializer
        if self.action == 'update' or self.action == 'partial_update':
            serializer = ProductUpdateSerializer

        return serializer

    @action(detail=True, methods=['put'], url_path='like')
    def like(self, request, pk):
        try:
            obj = self.get_object()
            user = request.user
            message = like_or_dislike(obj, user)
            return Response(message, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product like error {str(e)}')
            raise Http404

    @action(detail=True, methods=['post'], url_path='images')
    def save_image(self, request, pk):
        try:
            product = self.get_object()
            _, message = save_image(product, request.data)
            if _:
                return Response(message, status=status.HTTP_200_OK)

            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_exception(e, f'Save image error {str(e)}')
            raise Http404


class ProductRetrieveViewSet(
    ProductContextSerializerMixins,
    generics.GenericAPIView
):
    serializer_class = ProductRetrieveSerializer
    authentication_classes = []
    permission_classes = []
    queryset = Product.with_related.all()

    def get(self, request, pk):
        try:
            context = self.get_serializer_context()
            user_id = context.get('user_id') if context is not None else None
            obj = get_product_by_id_user_id(pk, user_id)
            if not obj.is_active:
                raise Http404

            serializer = self.get_serializer(obj, context={'user_id': user_id})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product details {str(e)}')
            raise Http404


class ProductListByFilterViewSet(
    ProductContextSerializerMixins,
    generics.GenericAPIView
):
    authentication_classes = []
    permission_classes = []
    serializer_class = ProductListSerializer
    allowed_methods = ["GET"]
    queryset = Product.active_related.all()
    pagination_class = None

    @swagger_auto_schema(manual_parameters=manual_parameters)
    def get(self, request):
        context = self.get_serializer_context()
        user_id = context.get('user_id') if context is not None else None
        q = get_query_filter(request)
        queryset = get_product_queryset(q, user_id)
        paginator, result_page = paginate_queryset(queryset, request)
        try:
            serializer = self.get_serializer(result_page, many=True)
        except Exception as e:
            log_exception(e, f'Product list error {str(e)}')
            serializer = self.get_serializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class ProductPreviewViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductPreviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductPreviewPermissions)
    queryset = Product.with_related.all()


class FavoritesViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Favorites.objects.select_related('owner', 'product', 'like').all()

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == 'get_products':
            serializer = ProductListSerializer
        elif self.action == 'get_product_bookings':
            serializer = CreateBookingSerializer
        elif self.action == 'set_main_image':
            serializer = None

        return serializer

    @swagger_auto_schema(manual_parameters=[limit, offset])
    @action(detail=False, methods=['get'], url_path='products')
    def favorite(self, request):
        try:
            user = request.user
            if not user:
                raise Http404

            products = get_favorite_products(user)
            products_data = get_favorite_products_data(products)
            paginator, result_page = paginate_queryset(products_data, request)
            serializer = self.get_serializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            log_exception(e, f'Product not found {str(e)}')
            raise Http404

    @action(detail=False, methods=['post'], url_path='set_main_image')
    def set_main_image(self, request, pk):
        try:
            image = get_object_or_404(Image, pk=pk)
            Image.objects.filter(product=image.product).update(is_label=False)
            update_instance(image, {'is_label': True})

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product not found {str(e)}')
            raise Http404

    @swagger_auto_schema(manual_parameters=[limit, offset, start_date, end_date])
    @action(detail=False, methods=['get'], url_path='get_product_bookings')
    def get_product_bookings(self, request, pk):
        try:
            product = get_object_or_404(Product.objects.prefetch_related('booking'), pk=pk)
            bookings = get_product_bookings(product, request)
            paginator, result_page = paginate_queryset(bookings, request)
            serializer = self.get_serializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            log_exception(e, f'Product not found {str(e)}')
            raise Http404

    @swagger_auto_schema(manual_parameters=[active])
    @action(detail=False, methods=['get'], url_path='get_products')
    def get_products(self, request):
        active = request.GET.get('active', True)
        try:
            user = request.user
            products = get_user_products(user)
            if active == 'false':
                products = products.filter(is_active=False)

            paginator, result_page = paginate_queryset(products, request)
            serializer = self.get_serializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            log_exception(e, f'Product not found {str(e)}')
            raise Http404


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, CommentPermissions)


class BookingViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticatedOrReadOnly)
    serializer_class = CreateBookingSerializer
    filterset_class = BookingFilterSet
    queryset = Booking.objects.all()


class CategoryViewSet(
    generics.ListAPIView,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)
    pagination_class = None


class TypeViewSet(
    generics.ListAPIView,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = TypeSerializer
    queryset = Type.objects.all()
    pagination_class = None


class ConvenienceViewSet(
    generics.ListAPIView,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = ConvenienceSerializer
    queryset = Convenience.objects.filter(is_active=True)
    pagination_class = None


class ImageViewSet(
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    authentication_classes = []
    permission_classes = []

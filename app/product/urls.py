from django.urls import path, include
from product.views import (
    ProductViewSet,
    ProductRetrieveViewSet,
    BookingViewSet,
    CategoryViewSet,
    CommentViewSet,
    ProductPreviewViewSet,
    FavoritesViewSet,
    ProductListByFilterViewSet,
    TypeViewSet,
    ConvenienceViewSet,
    ImageViewSet,
)
from product.sitemap import ProductSitemap
from django.contrib.sitemaps.views import sitemap

from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=True)
router.register('products/images', ImageViewSet, basename='images')
router.register('products', ProductViewSet, basename='products')
router.register('products/preview', ProductPreviewViewSet, basename='preview')
router.register('booking', BookingViewSet, basename='booking')
router.register('categories', CategoryViewSet, basename='categories')
router.register('comments', CommentViewSet, basename='comments')
router.register('conveniences', ConvenienceViewSet, basename='conveniences')
router.register('types', TypeViewSet, basename='types')

urlpatterns = [
    path('', include(router.urls)),
    path('products/get', ProductListByFilterViewSet.as_view()),
    path('products/<int:pk>', ProductRetrieveViewSet.as_view()),
    path('user/favorite/products', FavoritesViewSet.as_view({"get": "favorite"})),
    path('user/products/<int:pk>/main-image', FavoritesViewSet.as_view({"post": "set_main_image"})),
    path('user/products/<int:pk>/booking', FavoritesViewSet.as_view({"get": "get_product_bookings"})),
    path('user/products', FavoritesViewSet.as_view({'get': 'get_products'})),

    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': {
            "static": ProductSitemap,
        }},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

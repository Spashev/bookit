from product.models import Product

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache


def get_products_from_cache_or_db():
    products = cache.get('products')
    if not products:
        products = list(Product.objects.all())
        cache.set('products', products)
    return products


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return get_products_from_cache_or_db()

    def location(self, obj):
        return f"{settings.SITEMAP_LINK}/{obj.pk}"

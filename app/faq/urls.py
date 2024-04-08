from django.urls import path, include
from rest_framework.routers import DefaultRouter

from faq.views import HelpCenterViewSet, FaqViewSet

router = DefaultRouter(trailing_slash=True)
router.register('help-center', HelpCenterViewSet, basename='help-center')
router.register('faq', FaqViewSet, basename='faq')

urlpatterns = [
    path('', include(router.urls)),
]

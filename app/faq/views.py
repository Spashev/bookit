from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions, status, generics

from faq.serializers import HelpCenterSerializer, FaqSerializer
from faq.models import HelpCenter, Faq


class HelpCenterViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = HelpCenterSerializer
    authentication_classes = []
    permission_classes = []
    queryset = HelpCenter.objects.all()


class FaqViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FaqSerializer
    authentication_classes = []
    permission_classes = []
    queryset = Faq.objects.all()

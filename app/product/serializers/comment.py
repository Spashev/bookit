from rest_framework import serializers
from product.models import Comment

from helpers.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    content = serializers.CharField(max_length=350)

    class Meta:
        model = Comment
        fields = (
            'product',
            'reply',
            'content',
            'user'
        )


class CommentListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = (
            'reply',
            'content',
            'user',
            'date_posted'
        )

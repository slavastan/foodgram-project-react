from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.models import Subscribe


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            subscriber=user, subscribe_on=obj
        ).exists()

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

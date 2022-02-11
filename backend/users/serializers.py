from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import Follow, User


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, user_object):
        return Follow.objects.filter(
            user=self.context["request"].user.id, follower=user_object.id
        ).exists()

    def get_recipes_count(self, user_object):
        return user_object.recipes.all().count()

    def get_recipes(self, user_object):
        from api.serializers import RecipeForListSerializer

        return RecipeForListSerializer(
            user_object.recipes.all(), read_only=True, many=True
        ).data


class RegistrationSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]


class UserRecipeSerializer(CustomUserSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

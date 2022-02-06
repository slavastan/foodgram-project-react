from django.contrib.auth import get_user_model
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCard, Subscribe, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = (
            validators.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('subscriber', 'subscribe_on'),
            ),
        )

    def validate(self, data):
        """Пользователь не может подписаться на самого себя"""
        if data['subscribe_on'] == self.context['request'].user:
            raise ValidationError("Вы не можете подписаться на самого себя")
        return data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredients.id', queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField(
        min_value=1,
        max_value=200000,
        error_messages={'min_value': ('Кол-во не может быть меньше 1')},
    )

    def validate_amount(self, value):
        if value < 1:
            raise validators.ValidationError(
                {'amount': 'Кол-во не может быть меньше 1'}
            )
        return value

    class Meta:
        model = RecipeIngredient
        exclude = ('recipes', 'ingredients')
        extra_kwargs = {
            'id': {'read_only': False},
            'amount': {
                'error_messages': {
                    'min_value': ('Нужен как минимум один ингредиент')
                }
            },
        }


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe',
        required=True,
    )
    tags = TagSerializer(many=True, required=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(use_url=True)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужен как минимум один ингредиент'
            )
        list_of_id = [_['ingredients']['id'] for _ in value]
        if len(list_of_id) != len(set(list_of_id)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужен как минимум один тег'
            )
        return value


    def save_ingredients(self, recipe, amounts_ingredients):
        amounts_instance = []
        for amount_ingredient in amounts_ingredients:
            amount = amount_ingredient["amount"]
            ingredient = amount_ingredient["id"]
            amounts_instance.append(
                RecipeIngredient(
                    amount=amount,
                    recipe=recipe,
                    ingredient=ingredient,
                )
            )
        RecipeIngredient.objects.bulk_create(amounts_instance)


    def create(self, validated_data):
        with transaction.atomic():
            recipe = validated_data.pop('recipe')
            saved_recipe = super().create(validated_data)
            self.save_ingredients(saved_recipe, recipe)
        return saved_recipe


    def update(self, instance, validated_data):
        with transaction.atomic():
            recipe = validated_data.pop('recipe', None)
            saved_recipe = super().update(instance, validated_data)
            if recipe:
                saved_recipe.recipe.all().delete()
                self.save_ingredients(instance, recipe)
        return saved_recipe


    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user, recipe__in=[obj.pk]
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCard.objects.filter(
            user=user, recipe__in=[obj.pk]
        ).exists()

    class Meta:
        model = Recipe
        fields = '__all__'
        extra_kwargs = {
            'cooking_time': {
                'error_messages': {
                    'min_value': ('Время приготовления не может быть меньше 0')
                }
            },
            "ingredients": {"error_messages": {"amount": "сообщение"}}
        }


class RecipeShortSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(CustomUserSerializer):
    recipes = RecipeShortSerializer(source='author', read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

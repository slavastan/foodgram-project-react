from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from .models import *
from users.serializers import CustomUserSerializer


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'

    def to_internal_value(self, data):
        try:
            tag = Tags.objects.get(id=data)
        except ObjectDoesNotExist:
            raise ValidationError('Wrong tag id')
        return tag


class SubscribesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribes
        fields = '__all__'
        validators = (
            validators.UniqueTogetherValidator(
                queryset=Subscribes.objects.all(),
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
        source='ingredients.id', queryset=Ingredients.objects.all()
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


class RecipesSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe',
        required=True,
    )
    tags = TagsSerializer(many=True, required=True)
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

    def create(self, validated_data):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(author=user, **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingr in ingredients:
            RecipeIngredient.objects.create(
                recipes=recipe,
                ingredients=ingr['ingredients']['id'],
                amount=ingr['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        tags_updated = validated_data.pop('tags')
        ingr_updated = validated_data.pop('recipe')

        for item in validated_data:
            if Recipes._meta.get_field(item):
                setattr(instance, item, validated_data[item])
            RecipeIngredient.objects.filter(recipes=instance).delete()
        instance.tags.clear()
        instance.tags.set(tags_updated)
        for ingr in ingr_updated:
            i = get_object_or_404(Ingredients, id=ingr['ingredients']['id'].id)
            RecipeIngredient.objects.create(
                recipes=instance, ingredients=i, amount=ingr['amount']
            )
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorites.objects.filter(
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
        model = Recipes
        fields = '__all__'
        extra_kwargs = {
            'cooking_time': {
                'error_messages': {
                    'min_value': ('Время приготовления не может быть меньше 0')
                }
            },
            "ingredients": {"error_messages": {"amount": "сообщение"}}
        }


class RecipeShortSerializer(RecipesSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(CustomUserSerializer):
    recipes = RecipeShortSerializer(source='author', read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj).count()

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


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'

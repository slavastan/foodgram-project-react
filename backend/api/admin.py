from django.contrib import admin

from .models import *


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'number_of_additions')
    empty_value_display = ('-empty-')
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='Number of additions in Favorites',)
    def number_of_additions(self, obj):
        """Сколько раз рецепт добавлялся в избранное"""

        return Favorites.objects.filter(recipe__in=[obj.pk]).count()


@admin.register(RecipeIngredient)
class RecipeIngredients(admin.ModelAdmin):
    list_display = ('ingredients', 'recipes', 'amount')
    empty_value_display = ('-empty-')
    search_fields = ('ingredients', 'recipes', 'amount')


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    empty_value_display = ('-empty-')
    list_filter = ('name',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    empty_value_display = ('-empty-')
    search_fields = ('name', 'color')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user',)
    empty_value_display = ('-empty-')
    search_fields = ('user',)

    @staticmethod
    def get_recipes(obj):
        """Рецепты в избранном"""
        return '\n'.join([_.name for _ in obj.recipe.all()])


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_recipes')
    empty_value_display = ('-empty-')
    search_fields = ('user', 'get_recipes')

    @staticmethod
    def get_recipes(obj):
        """Рецепты в списке покупок"""
        return '\n'.join([_.name for _ in obj.recipe.all()])


@admin.register(Subscribes)
class SubscribesAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribe_on')
    empty_value_display = ('-empty-')
    search_fields = ('subscriber', 'subscribe_on')

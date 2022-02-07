from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCard,
    Subscribe,
    Tag,
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("author", "name", "number_of_additions")
    empty_value_display = "-empty-"
    list_filter = ("name", "author", "tags")

    @admin.display(
        description="Number of additions in Favorites",
    )
    def number_of_additions(self, obj):
        """Сколько раз рецепт добавлялся в избранное"""
        return Favorite.objects.filter(recipe=obj.pk).count()


@admin.register(RecipeIngredient)
class RecipeIngredient(admin.ModelAdmin):
    list_display = ("ingredient", "recipe", "amount")
    empty_value_display = "-empty-"
    search_fields = ("ingredient", "recipe", "amount")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    empty_value_display = "-empty-"
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color")
    empty_value_display = "-empty-"
    search_fields = ("name", "color")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_recipes",
    )
    empty_value_display = "-empty-"
    search_fields = ("user", "get_recipes")

    @staticmethod
    def get_recipes(obj):
        """Рецепты в избранном"""
        user_favorites = Favorite.objects.filter(user=obj.user).values(
            "recipe__name"
        )
        return [i["recipe__name"] for i in user_favorites]


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ("user", "get_recipes")
    empty_value_display = "-empty-"
    search_fields = ("user", "get_recipes")

    @staticmethod
    def get_recipes(obj):
        """Рецепты в списке покупок"""
        user_shopping_card = ShoppingCard.objects.filter(user=obj.user).values(
            "recipe__name"
        )
        return [i["recipe__name"] for i in user_shopping_card]


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "subscribe_on")
    empty_value_display = "-empty-"
    search_fields = ("subscriber", "subscribe_on")

from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingList,
    Tag,
)


class TagAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    search_fields = ["name", "author__username", "tags__name"]


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingList)

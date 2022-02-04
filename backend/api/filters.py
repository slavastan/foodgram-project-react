from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Recipes


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                recipe_in_shopping_card__user=self.request.user
            )
        return queryset.filter(
            ~Q(recipe_in_shopping_card__user=self.request.user)
        )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(recipes_in_favorite__user=self.request.user)
        return queryset.filter(~Q(recipes_in_favorite__user=self.request.user))

    class Meta:
        model = Recipes
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteCreateDestroy, IngredientViewSet, RecipeViewSet,
                    ShoppingListCreateDestroy, TagViewSet)

router_v1 = DefaultRouter()

router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    path(
        '', include(router_v1.urls),
    ),
    re_path(
        r'recipes/(?P<recipe_id>\d+)/favorite/',
        FavoriteCreateDestroy.as_view(),
        name='favorite',
    ),
    re_path(
        r'recipes/(?P<recipe_id>\d+)/shopping_cart/',
        ShoppingListCreateDestroy.as_view(),
        name='shopping-list',
    ),
]

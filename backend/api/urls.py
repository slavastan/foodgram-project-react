from django.urls import include, path, re_path
from rest_framework import routers

from . import views

router_v1 = routers.DefaultRouter()

router_v1.register('subscribes', views.SubscribeViewSet, basename='subs')
router_v1.register('recipes', views.RecipeView, basename='recipes')
router_v1.register('tags', views.TagViewSet, basename='tags')
router_v1.register(
    'ingredients', views.IngredientViewSet, basename='ingredients'
)

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        views.download_shopping_card,
        name='download_shopping_card',
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        views.get_or_delete_obj,
        {'model': 'ShoppingCard'},
        name='shopping_cart',
    ),
    path(
        'recipes/<int:pk>/favorite/',
        views.get_or_delete_obj,
        {'model': 'Favorite'},
        name='favorites',
    ),
    re_path('', include(router_v1.urls)),
]

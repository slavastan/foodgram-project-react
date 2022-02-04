from rest_framework import routers
from django.urls import include, path, re_path
from . import views

router_v1 = routers.DefaultRouter()

router_v1.register('subscribes', views.SubscribesViewSet, basename='subs')
router_v1.register('recipes', views.RecipesView, basename='recipes')
router_v1.register('tags', views.TagsViewSet, basename='tags')
router_v1.register(
    'ingredients', views.IngredientsViewSet, basename='ingredients'
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
        {'model': 'Favorites'},
        name='favorites',
    ),
    re_path('', include(router_v1.urls)),
]

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import Ingredients, Recipes, Subscribes, Tags
from .serializers import *
from users.models import User
from .filters import RecipeFilter
from .permissions import RecipePermissions


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    model = Ingredients
    serializer_class = IngredientsSerializer
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    model = Tags
    serializer_class = TagsSerializer
    pagination_class = None


class SubscribesViewSet(viewsets.ModelViewSet):
    queryset = Subscribes.objects.all()
    model = Subscribes
    serializer_class = SubscribesSerializer
    pagination_class = None


class RecipesView(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    model = Recipes
    serializer_class = RecipesSerializer
    permission_classes = (RecipePermissions,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering = ["-pk"]


@api_view(["GET", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def get_or_delete_obj(request, **kwargs):
    """Для ShoppingCard и Favorites.
    Создает объект данной модели по запросу GET
    или удаляет его по запросу DELETE.
    """
    model = apps.get_model('api', kwargs['model'])
    id_recipe = kwargs.get('pk')
    recipe = get_object_or_404(Recipes, id=id_recipe)
    ser = RecipeShortSerializer(recipe, context={'request': request})
    if request.method == "GET":
        obj, created = model.objects.get_or_create(user=request.user)
        if created:
            obj.recipe.add(recipe)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        if obj.recipe.filter(pk=recipe.pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        obj.recipe.add(recipe)
        return Response(ser.data, status=status.HTTP_201_CREATED)
    elif request.method == "DELETE":
        try:
            obj = model.objects.get(recipe=recipe, user=request.user)
            obj.recipe.remove(recipe)
            return Response(data=None, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def download_shopping_card(request, **kwargs):
    """Pdf-файл со всеми ингредиентами списка покупок"""
    result_ingr = (
        Recipes.objects.filter(recipe_in_shopping_card__user=request.user)
        .order_by("ingredients__name")
        .values("ingredients__name", "ingredients__measurement_unit")
        .annotate(total=Sum("recipe__amount"))
    )
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="ShoppingCart.pdf"'
    p = canvas.Canvas(response)
    pdfmetrics.registerFont(TTFont("DejaVuSans", "./DejaVuSans.ttf"))
    p.setFont("DejaVuSans", 32)
    textobject = p.beginText(2 * cm, 29.7 * cm - 2 * cm)
    for result in result_ingr:
        textobject.textLine(
            f"{result['ingredients__name']}, "
            f"{result['ingredients__measurement_unit']} --- {result['total']}"
        )
    p.drawText(textobject)
    p.showPage()
    p.save()
    return response


class ListSubscribesView(generics.ListAPIView):
    serializer_class = UserSubscribeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(subscribe_on__subscriber=self.request.user)


@api_view(["GET", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def get_or_delete_sub(request, **kwargs):
    """Для Subscribes.
    Создает объект данной модели по запросу GET
    или удаляет его по запросу DELETE.
    """
    user_to_subscribe = get_object_or_404(User, pk=kwargs['pk'])
    ser = UserSubscribeSerializer(
        user_to_subscribe, context={'request': request}
    )
    if request.method == "GET":
        try:
            _, created = Subscribes.objects.get_or_create(
                subscriber=request.user, subscribe_on=user_to_subscribe
            )
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if created:
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        try:
            obj = Subscribes.objects.get(
                subscriber=request.user, subscribe_on=user_to_subscribe
            )
            obj.delete()
            return Response(data=None, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)

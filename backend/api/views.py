from django.apps import apps
from django.core.exceptions import BadRequest
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from users.models import User
from .filters import RecipeFilter
from .models import Ingredient, Recipe, Subscribe, Tag
from .permissions import RecipePermission
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, SubscribeSerializer,
                          TagSerializer, UserSubscribeSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    model = Ingredient
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    model = Tag
    serializer_class = TagSerializer
    pagination_class = None


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    model = Subscribe
    serializer_class = SubscribeSerializer
    pagination_class = None


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    model = Recipe
    serializer_class = RecipeSerializer
    permission_classes = (RecipePermission,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering = ["-pk"]


@api_view(["GET", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def get_or_delete_obj(request, **kwargs):
    model = apps.get_model('api', kwargs['model'])
    id_recipe = kwargs.get('pk')
    recipe = get_object_or_404(Recipe, id=id_recipe)
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
        except BadRequest:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST) 


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def download_shopping_card(request, **kwargs):
    result_ingr = (
        Recipe.objects.filter(recipe_in_shopping_card__user=request.user)
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
    user_to_subscribe = get_object_or_404(User, pk=kwargs['pk'])
    ser = UserSubscribeSerializer(
        user_to_subscribe, context={'request': request}
    )
    if request.method == "GET":
        try:
            _, created = Subscribe.objects.get_or_create(
                subscriber=request.user, subscribe_on=user_to_subscribe
            )
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if created:
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        try:
            obj = Subscribe.objects.get(
                subscriber=request.user, subscribe_on=user_to_subscribe
            )
            obj.delete()
            return Response(data=None, status=status.HTTP_204_NO_CONTENT)
        except BadRequest:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)

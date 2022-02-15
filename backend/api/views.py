import io

from django.db.models import Sum
from django.http.response import FileResponse
from fpdf import FPDF
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Tag
from .paginations import Pagination
from .permissions import IsAuthor
from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeForListSerializer,
    RecipeSerializer,
    TagSerializer,
)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-pub_date")
    serializer_class = RecipeSerializer
    pagination_class = Pagination
    permission_classes_by_action = {
        "create": [IsAuthenticated],
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "partial_update": [IsAuthor],
        "update": [IsAuthor],
        "destroy": [IsAuthor],
    }
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return RecipeCreateUpdateSerializer
        else:
            return RecipeSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        ingredients_amounts = (
            Recipe.objects.filter(shopping_list__user=request.user)
            .order_by("ingredients__name")
            .values("ingredients__name", "ingredients__measurement_unit")
            .annotate(amount=Sum("amount_ingredients__amount"))
        )

        pdf = FPDF()
        pdf.add_font(
            "DejaVu", "", "./api/fonts/DejaVuSansCondensed.ttf", uni=True
        )
        pdf.set_font("DejaVu", "", 14)
        pdf.add_page()
        for item in ingredients_amounts:
            name, amount, measurement_unit = (
                item["ingredients__name"],
                item["amount"],
                item["ingredients__measurement_unit"],
            )
            text = f"{name} ({measurement_unit}) - {amount}"

            pdf.cell(0, 10, txt=text, ln=1)

        string_file = pdf.output(dest="S")
        response = FileResponse(
            io.BytesIO(string_file.encode("latin1")),
            content_type="application/pdf",
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopong-list.pdf"'

        return response

    def favorite_and_shopping(self, related):
        recipe = self.get_object()
        if self.request.method == "DELETE":
            related.objects.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if related.objects.filter(recipe=recipe).exist():
            raise validators.ValidationError('Уже существует')
        related.objects.create(recipe=recipe)
        serializer = RecipeForListSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            name='favorite')
    def favorite(self, request, pk=None):
        return self.favorite_and_shopping(request.user.favorites_recipes)

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            name='shopping_cart')
    def shopping_cart(self, request, pk=None):
        return self.favorite_and_shopping(request.user.shopping_user)

import io

from django.db.models import Sum
from django.http.response import FileResponse
from fpdf import FPDF
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from .paginations import Pagination
from .permissions import IsAuthor
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeForListSerializer, RecipeSerializer,
                          TagSerializer)


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
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    pagination_class = Pagination
    permission_classes_by_action = {
        'create': [IsAuthenticated],
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'partial_update': [IsAuthor],
        'update': [IsAuthor],
        'destroy': [IsAuthor],
    }
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipeCreateUpdateSerializer
        else:
            return RecipeSerializer

    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        create_serializer = RecipeCreateUpdateSerializer(
            data=request.data, *args, **kwargs
        )
        create_serializer.is_valid(raise_exception=True)
        recipe = create_serializer.save(author=self.request.user)

        retrieve_serializer = RecipeSerializer(
            instance=recipe, *args, **kwargs
        )
        headers = self.get_success_headers(retrieve_serializer.data)
        return Response(
            retrieve_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs.pop('pk')

        instance = self.get_object()
        update_serializer = RecipeCreateUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
        )
        update_serializer.is_valid(raise_exception=True)
        instance = update_serializer.save(author=self.request.user)
        retrieve_serializer = RecipeSerializer(
            instance=instance, **kwargs
        )

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(retrieve_serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients_amounts = Recipe.objects.filter(
            shopping_list__user=request.user
        ).order_by('ingredients__name').values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount_ingredients__amount'))

        pdf = FPDF()
        pdf.add_font(
            "DejaVu", "", "./api/fonts/DejaVuSansCondensed.ttf", uni=True
        )
        pdf.set_font("DejaVu", "", 14)
        pdf.add_page()
        for item in ingredients_amounts:
            name, amount, measurement_unit = (
                item['ingredients__name'], item['amount'], item[
                    'ingredients__measurement_unit'
                ]
            )
            text = f'{name} ({measurement_unit}) - {amount}'

            pdf.cell(0, 10, txt=text, ln=1)

        string_file = pdf.output(dest='S')
        response = FileResponse(
            io.BytesIO(string_file.encode('latin1')),
            content_type='application/pdf',
        )
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopong-list.pdf"'

        return response


class FavoriteCreateDestroy(GenericAPIView):
    def get(self, request, recipe_id):
        kwargs = {'context': self.get_serializer_context()}
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if not Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeForListSerializer(instance=recipe, **kwargs)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response('Уже в избранных', status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        if Favorite.objects.filter(
            user=request.user,
            recipe_id=recipe_id
        ).exists():
            Favorite.objects.filter(
                user=request.user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Уже удален из избранных', status.HTTP_400_BAD_REQUEST)


class ShoppingListCreateDestroy(GenericAPIView):
    def get(self, request, recipe_id):
        kwargs = {'context': self.get_serializer_context()}
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if not ShoppingList.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            ShoppingList.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = RecipeForListSerializer(instance=recipe, **kwargs)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response('Уже в корзине', status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        if ShoppingList.objects.filter(
            user=request.user,
            recipe_id=recipe_id
        ).exists():
            ShoppingList.objects.filter(
                user=request.user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Уже удален из корзины', status.HTTP_400_BAD_REQUEST)

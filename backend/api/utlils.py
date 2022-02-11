from .models import Ingredient, IngredientAmount


def ingredient_creaton(recipe, ingredients):
    amounts_instance = []
    for ingredient_data in ingredients:
        amount = ingredient_data['amount']
        amounts_instance.append(
            IngredientAmount(
                amount=amount,
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    pk=ingredient_data['id']
                ),
            )
        )
    return IngredientAmount.objects.bulk_create(amounts_instance)

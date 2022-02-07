from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингредиента", max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения", max_length=200
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name=("Название тега"), max_length=200)
    color = ColorField(verbose_name=("Цветовой HEX-код"), max_length=7)
    slug = models.SlugField(verbose_name=("Slug"), max_length=50)

    class Meta:
        ordering = ("name",)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.SET_NULL,
        null=True,
        related_name="author",
    )
    tags = models.ManyToManyField(
        Tag, verbose_name=("Тег рецепта"), blank=True
    )
    image = models.ImageField()
    name = models.CharField(verbose_name="Название рецепта", max_length=200)
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=("Время приготовления в минутах"),
        validators=(
            MinValueValidator(1, message=("Укажите время приготовления")),
        ),
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="ingredient",
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="recipe",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    amount = models.SmallIntegerField(
        validators=(
            MinValueValidator(1, message=("Укажите верное количество")),
        ),
        verbose_name="Количество рецептурных ингредиентов",
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингридиенты рецепта"
        constraints = [models.UniqueConstraint(
            fields=["ingredient", "recipe"], name="unique_recipeingridient"
        )]

    def __str__(self):
        return ("Ingredients for recipe {}").format(self.recipe.name)


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=("Подписчик"),
        related_name="subscriber",
    )
    subscribe_on = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=("Подписаться"),
        related_name="subscribe_on",
    )

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"
        constraints = [models.UniqueConstraint(
            fields=["subscriber", "subscribe_on"], name="unique_subscribe"
        )]

    def __str__(self) -> str:
        return f"{self.subscriber} subscribed on {self.subscribe_on}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=("Список избранного пользователя"),
        on_delete=models.CASCADE,
        related_name="recipes_of_user_favorite",
    )
    recipe = models.ManyToManyField(
        Recipe,
        verbose_name=("Избранные рецепты"),
        related_name="recipes_in_favorite",
    )

    class Meta:
        ordering = ("recipe__name",)
        verbose_name = "Список избранного"
        verbose_name_plural = "Список избранного"


class ShoppingCard(models.Model):
    recipe = models.ForeignKey( 
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт списка покупок", 
        related_name="recipe_in_shopping_card", 
    ) 
    user = models.ForeignKey(
        User,
        verbose_name=("Список покупок пользователя"),
        on_delete=models.CASCADE,
        related_name="shopping_card",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        constraints = [models.UniqueConstraint(
            fields=["user", "recipe"], name="unique_shoppingcard"
        )]

    def __str__(self) -> str:
        return ("{}'s shopping card").format(self.user.username)

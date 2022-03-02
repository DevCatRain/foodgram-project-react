from colorfield.fields import ColorField

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .validators import min_cooking_time

MIN_AMOUNT = 'Количество ингредиента должно быть больше нуля'

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='uniq_measurement_unit')
        ]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Тег',
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Адрес',
        unique=True
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет тега',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    image = models.ImageField(
        upload_to='media/recipes/images/',
        verbose_name='Картинка',
        help_text='Загрузите изображение'
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipe_ingredients',
        through='AmountOfIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe_tag',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1), min_cooking_time],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class AmountOfIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='amount_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='amount_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(0)],
        error_messages={'validators': MIN_AMOUNT},
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='uniq_ingredient_in_recipe')
        ]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='uniq_favorite')
        ]


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Покупатель'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'],
                                    name='uniq_recipe_in_cart')
        ]

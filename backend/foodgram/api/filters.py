# Все импорты отсортированы с помощью isort .
# Проходят автоматическую проверку flake8 при деплое.
# Отдельно дополнительно проверила через сервис http://pep8online.com/.
# Что с ними не так?
from django_filters import rest_framework

from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(field_name='name',
                                     lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(rest_framework.FilterSet):
    """ Фильтрация рецептов по избранному, автору, списку покупок и тегам.
    """
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = rest_framework.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart_recipe__user=user)
        return queryset

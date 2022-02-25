from functools import reduce

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Sum
from django.http import HttpResponse

from .filters import IngredientFilter, RecipeFilter
from .mixins import CreateListViewSet
from .models import Ingredient, Recipe, Tag
from .paginator import CustomPaginator
from .permissions import AuthorOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeSerializer, TagSerializer,
)

ALREADY_ADD_RECIPE = 'Этот рецепт уже добавлен'
ERROR_ADD_RECIPE = 'Этот рецепт не был добавлен'
TITLE = 'Ваш список покупок:\n\n'


class RecipeViewSet(viewsets.ModelViewSet):

    """ Страница со всеми рецептами с паджинацией по 6 рецептов на странице.
    Сортировка от новых к старым.
    Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    Методы GET, POST, PATCH, DELETE.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPaginator
    permission_classes = (AuthorOrReadOnly,)
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def _add_recipe_in(self, request, related_manager):
        recipe = self.get_object()
        if request.method == 'POST':
            if related_manager.filter(recipe=recipe).exists():
                return Response(ALREADY_ADD_RECIPE,
                                status=status.HTTP_400_BAD_REQUEST)
            new_one = related_manager.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(new_one)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if related_manager.filter(recipe=recipe).exists():
            related_manager.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(ERROR_ADD_RECIPE, status=status.HTTP_400_BAD_REQUEST)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'],
            detail=True)
    def favorite(self, request, pk):
        return self._add_recipe_in(request, request.user.favorite_user)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'],
            detail=True)
    def shopping_cart(self, request, pk):
        return self._add_recipe_in(request, request.user.shopping_cart_user)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['GET'],
            detail=False)
    def download_shopping_cart(self, request):
        text = TITLE
        user = request.user
        ingredients = Recipe.objects.filter(
            shopping_cart_recipe__user=user
        ).values('ingredients__name',
                 'ingredients__measurement_unit').annotate(
                     amount=Sum('amount_recipe__amount'))

        ingredients_list = {}
        for ingredient in ingredients:
            key = (f'{ingredient["ingredients__name"]}, '
                   f'{ingredient["ingredients__measurement_unit"]}')
            if key in ingredients_list:
                ingredients_list[key] += ingredient['amount']
            else:
                ingredients_list[key] = ingredient['amount']

        text += reduce(
            lambda x, key:
            x + '   ' + key + ' -- ' + str(ingredients_list[key]) + '\n',
            ingredients_list, '')

        response = HttpResponse(text, content_type='text/plain; charset=utf-8')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientViewSet(viewsets.ModelViewSet):

    """ Список ингредиентов с возможностью поиска по имени.
    Страница доступна всем пользователям.
    Метод GET.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_class = IngredientFilter
    search_field = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):

    """ Позволяет устанавливать теги на рецептах.
    Страница доступна всем пользователям.
    Метод GET.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class FavoriteViewSet(CreateListViewSet):

    """ Позволяет добавлять/удалять понравившиеся рецепты в избранное.
    Доступно только авторизованному пользователю.
    Методы POST, DELETE.
    """

    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return self.request.user.favorite_recipe.all()

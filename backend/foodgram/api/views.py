from django.db.models import Sum
from django.http import HttpResponse

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.mixins import CreateListViewSet
from api.models import (Ingredient, Recipe, Tag)
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, FavoriteSerializer,
                             RecipeSerializer, TagSerializer)

ALREADY_ADD_RECIPE = 'Этот рецепт уже добавлен'
ERROR_ADD_RECIPE = 'Этот рецепт не был добавлен'


class RecipeViewSet(viewsets.ModelViewSet):

    """ Страница со всеми рецептами с паджинацией по 6 рецептов на странице.
    Сортировка от новых к старым.
    Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
        text = 'Ваш список покупок:\n\n'
        user = self.request.user
        ingredients = Recipe.objects.filter(
            shopping_cart_recipe__user=user
        ).values('ingredients__name',
                 'ingredients__measurement_unit').annotate(
                     amount=Sum('amountofingredient__amount'))

        text += '\n'.join([
            f'{ingredient["ingredients__name"]} '
            f'({ingredient["ingredients__measurement_unit"]}) — '
            f'{ingredient["amount"]}\n' for ingredient in ingredients
        ])

        response = HttpResponse(text, content_type='text/plain; charset=utf-8')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientViewSet(viewsets.ModelViewSet):

    """ Список ингредиентов с возможностью поиска по имени.
    Страница доступна всем пользователям.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):

    """ Позволяет устанавливать теги на рецептах.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FavoriteViewSet(CreateListViewSet):

    """ Позволяет добавлять понравившиеся рецепты в избранное.
    """

    serializer_class = FavoriteSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return self.request.user.favorite_recipe.all()

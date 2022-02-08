from django.contrib.auth import get_user_model
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from functools import reduce
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.mixins import CreateListViewSet
from api.models import (AmountOfIngredient, Ingredient, Favorite,
                        Recipe, ShoppingCart, Tag)
from api.serializers import (IngredientSerializer, FavoriteSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             TagSerializer)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):

    """ Страница со всеми рецептами с паджинацией по 6 рецептов на странице.
    Сортировка от новых к старым.
    Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'],
            detail=True)
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = user.favorite_user.filter(recipe=recipe)

        if request.method == 'POST':
            if favorite.exists():
                return Response('Этот рецепт уже добавлен в избранное',
                                status=status.HTTP_400_BAD_REQUEST)
            new_fav = Favorite.objects.create(
                user=user, recipe=recipe
            )
            serializer = FavoriteSerializer(new_fav)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if favorite.exists():
            favorite.delete()
            return Response('Вы убрали этот рецепт из избранного',
                            status=status.HTTP_204_NO_CONTENT)
        return Response('Этот рецепт не был добавлен в избранное',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'],
            detail=True)
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        cart = user.shopping_cart_user.filter(recipe=recipe)

        if request.method == 'POST':
            if cart.exists():
                return Response('Этот рецепт уже добавлен в корзину',
                                status=status.HTTP_400_BAD_REQUEST)
            new_recipe = ShoppingCart.objects.create(
                user=user, recipe=recipe
            )
            serializer = ShoppingCartSerializer(new_recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if cart.exists():
            cart.delete()
            return Response('Рецепт успешно удален из корзины',
                            status=status.HTTP_204_NO_CONTENT)
        return Response('Этого рецепта нет в вашей корзине',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['GET'],
            detail=False)
    def download_shopping_cart(self, request):
        text = 'Ваш список покупок:\n\n'
        user = request.user
        ingredients = AmountOfIngredient.objects.filter(
            recipe__shopping_cart_recipe__user=user
        ).annotate(ing_name=F('ingredient__name'),
                   ing_m_u=F('ingredient__measurement_unit'),
                   ing_amount=F('amount'))

        ingredients_list = {}
        for ingredient in ingredients:
            key = f'{ingredient.ing_name}, {ingredient.ing_m_u}'
            if key in ingredients_list:
                ingredients_list[key] += ingredient.ing_amount
            else:
                ingredients_list[key] = ingredient.ing_amount

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

from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, FavoriteViewSet,
                       RecipeViewSet, TagViewSet)


app_name = 'api'

router = routers.DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet, basename='favorits'
)

urlpatterns = [
    path('', include(router.urls))
]

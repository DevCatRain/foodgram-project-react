from django.contrib.auth import get_user_model
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from .models import (
    AmountOfIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.serializers import UserSerializer

MIN_INGREDIENT = 'Должен быть хотя бы один ингредиент в рецепте'
DOUBLE_INGREDIENT = 'Ингредиенты не должны повторяться'
NO_INGREDIENT = 'Такого ингредиента нет в списке'
MIN_AMOUNT = 'Количество ингредиента должно быть больше нуля'
DOUBLE_RECIPE = 'У вас уже есть'
MIN_TAG = 'Установите хотя бы один тег'
DOUBLE_TAG = 'Теги не должны повторяться'
COOK_TIME = 'Укажите время приготовления блюда'
ALREADY_ADD_RECIPE = 'Вы уже добавили этот рецепт'

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountOfIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = AmountOfIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = AmountOfIngredient.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(MIN_INGREDIENT)
        ingredients_set = []
        for ingredient in value:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(MIN_AMOUNT)
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(DOUBLE_INGREDIENT)
            else:
                ingredients_set.append(ingredient['id'])
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError({'tags': MIN_TAG})

        if len(value) != len(set(value)):
            raise serializers.ValidationError({'tags': DOUBLE_TAG})

        return value

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def add_ingredients_in_recipe(self, recipe, ingredients):
        for item in ingredients:
            item_id = item['id']
            amount = item['amount']
            if AmountOfIngredient.objects.filter(recipe=recipe,
                                                 ingredient=item_id).exists():
                amount += F('amount')
            AmountOfIngredient.objects.update_or_create(
                recipe=recipe, ingredient=item_id,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients_in_recipe(recipe, ingredients)
        return recipe

    def update(self, instanse, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        AmountOfIngredient.objects.filter(recipe=instanse).delete()
        self.add_ingredients_in_recipe(instanse, ingredients)
        instanse.tags.set(tags)
        super().update(instanse, validated_data)
        return instanse


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message=ALREADY_ADD_RECIPE
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message=ALREADY_ADD_RECIPE
            )
        ]

    def to_representation(self, obj):
        return {
            'id': obj.recipe.id,
            'name': obj.recipe.name,
            'image': obj.recipe.image.url,
            'cooking_time': obj.recipe.cooking_time,
        }

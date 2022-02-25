from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from django.contrib.auth import get_user_model

from api.models import (
    AmountOfIngredient, Favorite, Ingredient, Recipe, ShoppingCart, Tag,
)
from users.serializers import UserSerializer

MIN_INGREDIENT = 'Должен быть хотя бы один ингредиент в рецепте'
DOUBLE_INGREDIENT = 'Ингредиенты не должны повторяться'
NO_INGREDIENT = 'Такого ингредиента нет в списке'
MIN_AMOUNT = 'Количество ингредиента должно быть больше нуля'
DOUBLE_RECIPE = 'У вас уже есть'
MIN_TAG = 'Установите хотя бы один тег'
DOUBLE_TAG = 'Теги не должны повторяться'
NO_TAG = 'Такого тега не существует'
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


class AmountOfIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_init'
    )

    class Meta:
        model = AmountOfIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('ingredient', 'recipe')
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = AmountOfIngredientSerializer(
        read_only=True, many=True,
        source='amount_recipe'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError({'tags': MIN_TAG})

        if len(data) != len(set(data)):
            raise serializers.ValidationError({'tags': DOUBLE_TAG})

        for tag_id in data:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f'{tag_id}: {NO_TAG}'
                )

        return data

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError({'ingredients': MIN_INGREDIENT})

        ids = [ing['id'] for ing in data]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                {'ingredients': DOUBLE_INGREDIENT}
            )

        for id in ids:
            if not Ingredient.objects.filter(id=id).exists():
                raise serializers.ValidationError(f'{id}: {NO_INGREDIENT}')

        amounts = [ing['amount'] for ing in data]
        for amount in amounts:
            if int(amount) <= 0:
                raise serializers.ValidationError({'amount': MIN_AMOUNT})

        return data

    def validate(self, data):
        data['ingredients'] = self.validate_ingredients(
            self.initial_data.get('ingredients')
        )
        data['tags'] = self.validate_tags(
            self.initial_data.get('tags')
        )

        author = self.context.get('request').user
        if self.context.get('request').method == 'POST':
            name = data.get('name')
            if Recipe.objects.filter(author=author, name=name).exists():
                raise serializers.ValidationError(
                    {f'рецепт {name} {DOUBLE_RECIPE}'}
                )
        data['author'] = author

        cooking_time = data.get('cooking_time')
        if cooking_time <= 0:
            raise serializers.ValidationError(COOK_TIME)

        return data

    def add_amount_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            AmountOfIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.add_amount_ingredient(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.add(*tags_data)

        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            AmountOfIngredient.objects.filter(recipe=instance).delete()
            self.add_amount_ingredient(ingredients_data, instance)

        return super().update(instance, validated_data)


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

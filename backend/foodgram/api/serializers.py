from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators
from .models import (AmountOfIngredient, Ingredient, Favorite,
                     Recipe, ShoppingCart, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')

    validators = [
        validators.UniqueTogetherValidator(
            queryset=Ingredient.objects.all(),
            fields=('name', 'measurement_unit')
        )
    ]


class AmountOfIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_init'
    )

    class Meta:
        model = AmountOfIngredient
        fields = ('id', 'name', 'measurement_unit')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('ingredient', 'recipe')
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    ingredients = AmountOfIngredientSerializer(
        many=True,
        read_only=True,
        source='amountofingredient_set'
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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()

    def validate_tags(self, value):
        tag_list = [tag for tag in value]
        if len(set(tag_list)) < len(tag_list):
            raise serializers.ValidationError(
                'Не может быть два одинаковых тега')
        return value

    def validate(self, data):
        serializer = RecipeSerializer(data=data, many=True)
        if serializer.is_valid():
            ingredients = serializer.validated_data.get('ingredients')
            tags = serializer.validated_data.get('tags')

            if ingredients is None:
                raise serializers.ValidationError(
                    {'ingredients': 'Должен быть '
                        'хотя бы один ингредиент в рецепте'}
                )
            for ingredient in ingredients:
                if int(ingredient.get('amount')) <= 0:
                    raise serializers.ValidationError(
                        {'amount': 'Количество ингредиента '
                            'должно быть больше нуля'}
                    )

            if tags is None:
                raise serializers.ValidationError(
                    {'tags': 'Должен быть хотя бы один тег'}
                )

        return serializer.validated_data

    def add_amount_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            AmountOfIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.add_amount_ingredient(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):

        tags_data = validated_data.get('tags')
        instance.tags.clear()
        instance.tags.add(*tags_data)

        ingredients_data = validated_data.get('ingredients')
        AmountOfIngredient.objects.filter(recipe=instance).delete()
        self.add_amount_ingredient(ingredients_data, instance)

        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

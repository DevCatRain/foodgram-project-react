from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, validators
from api.models import Recipe
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj.author
        ).exists()


class UserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            message='Этот email уже зарегистрирован')]
    )
    username = serializers.CharField(
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            message='Это имя пользователя уже используется')]
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'password')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на автора'
            )
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.author.recipe_author.all()
        if request:
            recipes_limit = self.context.get('recipes_limit')
            queryset = Recipe.objects.filter(author=obj.author)

            if recipes_limit is not None:
                queryset = Recipe.objects.filter(
                    author=obj.author
                )[:int(recipes_limit)]

        return FollowRecipesSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipe_author.count()

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя'
            )
        return data


class FollowRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

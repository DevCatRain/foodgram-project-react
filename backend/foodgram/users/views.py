from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from users.models import Follow
from users.serializers import FollowSerializer, UserSerializer


User = get_user_model()


class UsersViewSet(UserViewSet):

    """
    Предоставляет возможность работать с объектами пользователей:
    чиать, создавать, редактировать, удалять.
    Базовый доступ - только для администратора.
    Действие 'me/' доступно для всех авторизованных пользователей,
    где доступно получить свои данные.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['GET'],
            detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['GET'],
            detail=False)
    def subscriptions(self, request):
        subsriptions = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(subsriptions)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'],
            detail=True)
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subsciption = user.user.filter(author=author)

        if request.method == 'POST':
            if subsciption.exists():
                return Response('Вы уже подписаны на этого автора',
                                status=status.HTTP_400_BAD_REQUEST)
            elif author == user:
                return Response('Нельзя подписаться на самого себя')

            new_sub = Follow.objects.create(
                user=user, author=author
            )
            serializer = FollowSerializer(new_sub)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if subsciption.exists():
            subsciption.delete()
            return Response('Вы успешно отписаны от этого автора',
                            status=status.HTTP_204_NO_CONTENT)
        return Response('Вы не подписаны на этого автора',
                        status=status.HTTP_400_BAD_REQUEST)

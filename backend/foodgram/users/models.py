from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Неверное значение'
            )
        ]
    )
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author',
                               verbose_name='автор')

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='uniq_following')
        ]
        ordering = ['-id']

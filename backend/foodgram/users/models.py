from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

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
        blank=False,
        unique=True,
    )
    role = models.CharField(
        'Роль',
        choices=ROLE_CHOICES,
        max_length=9,
        default=USER,
        error_messages={'validators': 'Выбрана несуществующая роль'}
    )

    def __str__(self) -> str:
        return self.username

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='uniq_following')
        ]

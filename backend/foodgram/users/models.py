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

    bio = None
    role = None

    def __str__(self) -> str:
        return self.username


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

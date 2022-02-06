from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        USER = 'user', 'User'

    email = models.EmailField('email address', unique=True)
    role = models.CharField(
        'role', choices=Role.choices, default=Role.USER, max_length=30
    )
    username = models.CharField(
        'username',
        unique=True,
        max_length=150,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z')],
        error_messages={
            "unique": ('Пользователь с таким именем уже существует'),
        },
    )
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

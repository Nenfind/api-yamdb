from random import randint

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserManager(BaseUserManager):
    """Менеджер пользователей."""

    def _create_user(self, email, username, **extra_fields):
        if not email:
            raise ValueError('Необходимо ввести электронную почту.')
        if not username:
            raise ValueError('Необходимо ввести имя пользователя.')
        email = self.normalize_email(email)
        secret = str(randint(100000, 999999))
        user = self.model(email=email, username=username, secret=secret, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, **extra_fields):
        return self._create_user(email, username, **extra_fields)

    def create_superuser(self, email, username, **extra_fields):
        superuser_fields = {
            'is_staff': True,
            'is_superuser': True,
            'role': User.Role.ADMIN
        }
        superuser_fields.update(extra_fields)

        return self._create_user(email, username, **superuser_fields)


class User(AbstractUser):
    """Класс пользователей."""

    bio = models.TextField('Биография', blank=True)
    email = models.EmailField(unique=True)
    objects = UserManager()
    secret = models.CharField(
        'Код подтверждения',
        max_length=6,
        blank=True,
        help_text='6-значный код подтверждения',
    )

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    role = models.CharField(
        'роль',
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text='Роль пользователя.'
    )

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс пользователей."""

    bio = models.TextField('Биография', blank=True)
    email = models.EmailField(unique=True)

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

class UserManager(BaseUserManager):
    """Менеджер пользователей."""

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Необходимо ввести электронную почту.')
        if not username:
            raise ValueError('Необходимо ввести имя пользователя.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        # Create a new dictionary to ensure role is set first
        superuser_fields = {
            'is_staff': True,
            'is_superuser': True,
            'role': User.Role.ADMIN  # This will NOT be overwritten
        }
        superuser_fields.update(extra_fields)  # Merge with any additional fields

        return self._create_user(email, username, password, **superuser_fields)
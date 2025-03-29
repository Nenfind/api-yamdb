from random import randint

from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    ValidationError
)
from django.db import models

from .constants import ROLE_MIN_LENGTH, USERNAME_MAX_LENGTH, MIN_COUNT_SCORE, MAX_COUNT_SCORE
from .validators import validate_username, validate_year


class User(AbstractUser):
    """Класс пользователей."""

    bio = models.TextField('Биография', blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(
        unique=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=[validate_username],
    )

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    role = models.CharField(
        'роль',
        max_length=max([len(role) for role in Role.choices]) + ROLE_MIN_LENGTH,
        choices=Role.choices,
        default=Role.USER,
        help_text='Роль пользователя.'
    )

    class Meta:
        ordering = ('username', 'email')

    @property
    def is_admin(self):
        if (self.role == 'admin'
            or self.is_superuser
            or self.is_staff):
            return True
        return False

    @property
    def is_moderator(self):
        if (self.role == 'moderator'
            or self.is_admin):
            return True
        return False


class Category(models.Model):
    """Модель категории произведения."""

    name = models.CharField(max_length=256, blank=False)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        """Мета-класс для категории."""
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    """Модель жанра произведения."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        """Мета-класс для жанра."""
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField('Произведение', max_length=256)
    year = models.IntegerField(
        'Год',
        validators=(validate_year,),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles'
    )
    description = models.TextField(blank=True,)

    class Meta:
        """Мета-класс для произведения."""
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Связь между произведениями и жанрами."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        """Мета-класс для связи жанров и произведений."""
        verbose_name = 'Связь жанра и произведения'
        verbose_name_plural = 'Связи жанров и произведений'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'genre'),
                name='unique_title_genre'
            ),
        )

class Review(models.Model):
    """Отзыв к произведению."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведения',
        related_name='reviews'
    )
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(
            MinValueValidator(
                MIN_COUNT_SCORE,
                message='Оценка не может быть меньше 1.'
            ),
            MaxValueValidator(
                MAX_COUNT_SCORE,
                message='Оценка не может быть больше 10.'
            )
        )
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_title'
            ),
        )

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title} - оценка {self.score}'


class Comment(models.Model):
    """Комментарии к отзывам."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзывы на произведения',
        related_name='comments'
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Комментарий от {self.author} к отзыву {self.review.id}'

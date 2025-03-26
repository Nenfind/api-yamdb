from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Title(models.Model):
    name = models.TextField(default='Что то')


class Review(models.Model):
    """Отзывы к произведению."""
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
            MinValueValidator(1, message='Оценка не может быть меньше 1.'),
            MaxValueValidator(10, message='Оценка не может быть больше 10.')
        )
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_title'
            ),
        )

    def save(self, *args, **kwargs):
        """При сохранении отзыва обновляем рейтинг."""
        super().save(*args, **kwargs)
        self.update_title_rating(self.title_id)

    def delete(self, *args, **kwargs):
        """При удалении отзыва обновляем рейтинг."""
        title_id = self.title_id
        super().delete(*args, **kwargs)
        self.__class__.update_title_rating(title_id)

    @classmethod
    def update_title_rating(cls, title_id=None):
        """Обновляет рейтинг произведения."""
        rating_title, _ = RatingTitle.objects.get_or_create(title_id=title_id)
        rating_title.update_rating()


class RatingTitle(models.Model):
    """Рейтинг на основе отзывов."""
    title = models.OneToOneField(
        Title,
        on_delete=models.CASCADE,
        related_name='title_rating',
        verbose_name='Произведение',
    )
    rating = models.IntegerField(
        'Рейтинг',
        null=True,
        blank=True,
        default=None
    )

    def update_rating(self):
        """Обновляет рейтинг на основе отзывов."""
        reviews = self.title.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('score'))['score__avg']
            self.rating = int(round(avg_rating))
        else:
            self.rating = None
        self.save()


class Comment(models.Model):
    """Коментарии к отзывам."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзывы на произведения',
        related_name='comments'
    )
    text = models.TextField('Текст коментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)

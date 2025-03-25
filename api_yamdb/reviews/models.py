from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


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
    score = models.IntegerField(
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
                fields=('author', 'titles'),
                name='unique_author_title'
            )
        )

    def save(self, *args, **kwargs):
        """При сохранении отзыва обновляем рейтинг."""
        super().save(*args, **kwargs)
        title_rating, created = RatingTitle.objects.get_or_create(
            title=self.titles)
        title_rating.update_rating()


class RatingTitle(models.Model):
    """Рейтинг на основе отзывов."""
    title = models.OneToOneField(
        Title,
        on_delete=models.CASCADE,
        related_name='title_rating',
        verbose_name='Произведение'
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
    reviews = models.ForeignKey(
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

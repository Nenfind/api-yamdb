from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Reviews(models.Model):
    """Отзывы к произведению."""
    titles = models.ForeignKey(
        Titles,
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


class RatingTitles(models.Model):
    """Рейтинг на основе отзывов."""
    title = models.OneToOneField(
        Titles,
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


class Comments(models.Model):
    """Коментарии к отзывам."""
    reviews = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        verbose_name='Отзывы на произведения'
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

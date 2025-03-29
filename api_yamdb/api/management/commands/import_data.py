import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from reviews.models import (Category, Genre, Title, GenreTitle,
                            Review, Comment, User)


class Command(BaseCommand):
    """Команда для импорта данных из CSV файлов в базу данных."""
    help = 'Импорт данных из CSV файлов с полной валидацией'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.import_users()
                self.import_categories()
                self.import_genres()
                self.import_titles()
                self.import_genre_titles()
                self.import_reviews()
                self.import_comments()
                self.stdout.write(self.style.SUCCESS(
                    'Данные успешно импортированы'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка импорта: {str(e)}'))

    def import_categories(self):
        """Импорт категорий из category.csv."""
        Category.objects.all().delete()
        with open('static/data/category.csv', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    Category.objects.create(
                        id=int(row['id']),
                        name=row['name'].strip(),
                        slug=row['slug'].strip()
                    )
                except Exception as e:
                    self.stdout.write(f"Ошибка в строке {row}: {str(e)}")

    def import_genres(self):
        """Импорт жанров из genre.csv."""
        Genre.objects.all().delete()
        with open('static/data/genre.csv', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    Genre.objects.create(
                        id=int(row['id']),
                        name=row['name'].strip(),
                        slug=row['slug'].strip()
                    )
                except Exception as e:
                    self.stdout.write(f"Ошибка в строке {row}: {str(e)}")

    def import_titles(self):
        """Импорт произведений и их связей с жанрами."""
        Title.objects.all().delete()
        GenreTitle.objects.all().delete()
        with open('static/data/titles.csv', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    if not all([row['name'].strip(),
                                row['year'],
                                row['category']]):
                        raise ValidationError("Отсутствуют обязательные поля")

                    title = Title.objects.create(
                        id=int(row['id']),
                        name=row['name'].strip(),
                        year=int(row['year']),
                        category=Category.objects.get(id=int(row['category'])),
                        description=row.get('description', '')
                    )

                    if 'genres' in row and row['genres']:
                        for genre_slug in row['genres'].split(','):
                            GenreTitle.objects.create(
                                title=title,
                                genre=Genre.objects.get(
                                    slug=genre_slug.strip())
                            )
                except Exception as e:
                    self.stdout.write(f"Ошибка в строке {row}: {str(e)}")

    def import_genre_titles(self):
        """Импорт связей между произведениями и жанрами из genre_title.csv."""
        with open('static/data/genre_title.csv', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    GenreTitle.objects.get_or_create(
                        title_id=int(row['title_id']),
                        genre_id=int(row['genre_id'])
                    )
                except Exception as e:
                    self.stdout.write(f"Ошибка в строке {row}: {str(e)}")

    def import_reviews(self):
        """Импорт отзывов из review.csv."""
        Review.objects.all().delete()
        with open('static/data/review.csv', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    author_id = int(row['author'])
                    if not User.objects.filter(id=author_id).exists():
                        continue

                    Review.objects.create(
                        id=int(row['id']),
                        title_id=int(row['title_id']),
                        text=row['text'].strip(),
                        author_id=author_id,
                        score=int(row['score']),
                        pub_date=timezone.now()
                    )
                except Exception as e:
                    self.stdout.write(f"Ошибка в строке {row}: {str(e)}")

    def import_comments(self):
        """Импорт комментариев из comments.csv."""
        Comment.objects.all().delete()
        with open('static/data/comments.csv', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    author_id = int(row['author'])
                    if not User.objects.filter(id=author_id).exists():
                        continue

                    Comment.objects.create(
                        id=int(row['id']),
                        review_id=int(row['review_id']),
                        text=row['text'].strip(),
                        author_id=author_id,
                        pub_date=timezone.now()
                    )
                except Exception as e:
                    self.stdout.write(f"Ошибка в строке {row}: {str(e)}")

    def import_users(self):
        """Импорт пользователей из users.csv."""
        User.objects.all().delete()
        with open('static/data/users.csv', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    user = User.objects.create(
                        id=int(row['id']),
                        username=row['username'],
                        email=row['email'],
                        role=row.get('role', 'user'),
                        bio=row.get('bio', ''),
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', '')
                    )
                    user.set_password('defaultpass')
                    user.save()
                except Exception as e:
                    self.stdout.write(f"Ошибка в строке {row}: {str(e)}")

"""Сериализаторы для категорий, жанров и произведений."""
from rest_framework import serializers
from django.utils import timezone

from .models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def to_representation(self, instance):
        """Преобразование вывода для соответствия Redoc."""
        rep = super().to_representation(instance)
        rep['genre'] = [{'name': g.name, 'slug': g.slug}
                        for g in instance.genre.all()]
        rep['category'] = {
            'name': instance.category.name,
            'slug': instance.category.slug
        }
        return rep

    def validate_year(self, value):
        """Проверка, что год выпуска не больше текущего."""
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего'
            )
        return value

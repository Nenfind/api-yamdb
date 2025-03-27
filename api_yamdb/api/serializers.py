"""Сериализаторы для категорий, жанров и произведений."""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from reviews.models import Comment, Review, Category, Genre, Title

User = get_user_model()


class ReviewsSerializer(serializers.ModelSerializer):
    """Сереализтор для работы с моделью отзыв."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сереализтор для работы с моделью коментарий."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'pub_date',
        )
        model = Comment
        read_only_fields = ('review',)


class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'first_name', 'last_name', 'bio',
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким никнеймом уже существует.'
            )
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя создать пользователя с никнеймом "me"!'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Этот электронный адрес уже занят.'
            )
        return value


class PublicUserSerializer(AdminUserSerializer):
    """Сериализатор для пользователей с укороченным выводом"""

    class Meta(AdminUserSerializer.Meta):
        fields = ('username', 'email')


class TokenCreationSerializer(serializers.Serializer):
    """Сериализатор для выдачи токенов"""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise AuthenticationFailed("Неправильный код подтверждения.")
        return data

    def create(self, validated_data):
        user = get_object_or_404(User, username=validated_data['username'])
        refresh = RefreshToken.for_user(user)
        return {'token': str(refresh.access_token)}


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
    """Сериализатор для произведений с рейтингом."""
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def get_rating(self, obj):
        """Безопасное получение рейтинга."""
        if hasattr(obj, 'rating_obj') and obj.rating_obj:
            return obj.rating_obj.rating
        return None

    def to_representation(self, instance):
        """Форматированный вывод для API."""
        rep = super().to_representation(instance)
        rep['genre'] = [{
            'name': genre.name,
            'slug': genre.slug
        } for genre in instance.genre.all()]

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

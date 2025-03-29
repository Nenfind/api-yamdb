"""Сериализаторы для категорий, жанров и произведений."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью отзыв."""

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

    def validate(self, data):
        """
        Проверяет, что пользователь не оставлял
        отзыв на это произведение ранее.
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            title_id = self.context['view'].get_title().id
            author = request.user
            if Review.objects.filter(
                title_id=title_id,
                author=author
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью комментарий."""

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'me' in self.context.get('request').path:
            self.fields['role'].read_only = True

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
            raise ValidationError("Неправильный код подтверждения.")
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
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        if hasattr(obj, 'title_rating'):
            return obj.title_rating.rating
        return None

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

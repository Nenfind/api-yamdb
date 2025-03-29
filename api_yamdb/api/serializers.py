"""Сериализаторы для категорий, жанров и произведений."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from api.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import validate_username

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
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date',
        )


class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'first_name', 'last_name', 'bio',
        )


class PublicUserSerializer(serializers.Serializer):
    """Сериализатор для самостоятельной регистрации пользователей."""

    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=(validate_username,),
    )
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
    )

    class Meta(AdminUserSerializer.Meta):
        fields = ('username', 'email')

    def create(self, validated_data):
        try:
            user, created = User.objects.get_or_create(
                username=validated_data['username'],
                email=validated_data['email'])
            self.send_email(user)
        except IntegrityError:
            raise serializers.ValidationError({
                'detail': 'Данные username или почта уже заняты.'
            })
        return user

    def send_email(self, user):
        send_mail(
            subject='Код подтверждения YaMDB',
            message=f'Привет, {user.username}!\n\n'
                    f'Ваш код подтверждения: {default_token_generator.make_token(user)}\n\n'
                    f'Используйте его для входа в систему.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )


class TokenCreationSerializer(serializers.Serializer):
    """Сериализатор для выдачи токенов"""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(
                user, data['confirmation_code']
        ):
            raise ValidationError("Неправильный код подтверждения.")
        return data

    def create(self, validated_data):
        user = get_object_or_404(User, username=validated_data['username'])
        access = AccessToken.for_user(user)
        return {'token': str(access)}


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

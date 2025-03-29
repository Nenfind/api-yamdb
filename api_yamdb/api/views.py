"""Представления для категорий, жанров и произведений."""
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    permissions,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsOwnerAdminModeratorOrReadOnly
)
from .serializers import (
    AdminUserSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    PublicUserSerializer,
    ReviewsSerializer,
    TitleSerializer,
    TokenCreationSerializer
)
from .viewsets import CategoryGenreViewSetBase

User = get_user_model()


class ReviewsViewSet(viewsets.ModelViewSet):
    """Управление отзывами на произведения."""

    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    serializer_class = ReviewsSerializer
    permission_classes = (IsOwnerAdminModeratorOrReadOnly,)

    def get_title(self):
        """Возвращает произведение по id из URL."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Список отзывов текущего произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создание отзыва с привязкой к автору и произведению."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """Управление комментариями к отзывам."""

    http_method_names = ('get', 'post', 'patch',
                         'delete', 'head', 'options')
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerAdminModeratorOrReadOnly,)

    def get_review(self):
        """Возвращает отзыв по id из URL """
        """(с проверкой принадлежности к произведению)."""
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(
            Review,
            id=review_id,
            title_id=title_id
        )

    def get_queryset(self):
        """Список комментариев текущего отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создание комментария с привязкой к автору и отзыву."""
        review = self.get_review()
        serializer.save(
            author=self.request.user,
            review=review
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False, methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=self.request.user.role)
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserCreateAPIView(APIView):
    """Самостоятельная регистрация пользователей."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = PublicUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TokenObtainView(generics.CreateAPIView):
    """Получение токена по никнейму и коду подтверждения."""

    serializer_class = TokenCreationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.save()
        return Response(token_data)


class CategoryViewSet(CategoryGenreViewSetBase):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSetBase):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""

    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.select_related(
        'category'
    ).annotate(
        rating=Avg('reviews__score')
    ).prefetch_related(
        'genre'
    ).order_by(
        'name', 'year'
    )

    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

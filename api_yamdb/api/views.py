"""Представления для категорий, жанров и произведений."""
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import (viewsets, generics, permissions,
                            status, filters)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .permissions import IsAdminOrReadOnly, IsOwnerAdminModeratorOrReadOnly, IsAdmin
from .filters import TitleFilter
from api.serializers import (CommentSerializer, ReviewsSerializer,
                             AdminUserSerializer, TokenCreationSerializer,
                             PublicUserSerializer, CategorySerializer,
                             GenreSerializer, TitleSerializer)
from reviews.models import Review, Category, Genre, Title


User = get_user_model()


class ReviewsViewSet(viewsets.ModelViewSet):
    """Управление отзывами на произведения."""
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
    search_fields = ['=username']
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(detail=False, methods=['get', 'patch'], permission_classes=(IsAuthenticated,))
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserCreateAPIView(generics.CreateAPIView):
    """Самостоятельная регистрация пользователей."""

    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        self.send_email(user)

    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.get(
                username=request.data.get('username'),
                email=request.data.get('email')
            )
            self.send_email(user)
            return Response(
                {'username': request.data.get(
                    'username'), 'email': request.data.get('email')},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            response = super().create(request, *args, **kwargs)
            response.status_code = status.HTTP_200_OK
            return response

    def send_email(self, user):
        send_mail(
            subject='Код подтверждения YaMDB',
            message=f'Привет, {user.username}!\n\n'
                    f'Ваш код подтверждения: {user.confirmation_code}\n\n'
                    f'Используйте его для входа в систему.',
            from_email='yamdb@ya.ru',
            recipient_list=[user.email],
            fail_silently=True,
        )

    def put(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Method "PUT" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class TokenObtainView(generics.CreateAPIView):
    """Получение токена по никнейму и коду подтверждения."""

    serializer_class = TokenCreationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.save()
        return Response(token_data)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

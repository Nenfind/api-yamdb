from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import viewsets, generics, permissions, mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.permissions import IsOwnerAdminModeratorOrReadOnly
from api.serializers import CommentSerializer, ReviewsSerializer, AdminUserSerializer, TokenCreationSerializer, PublicUserSerializer
from reviews.models import Review, Title

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
                {'username': request.data.get('username'), 'email': request.data.get('email')},
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

class TokenObtainView(generics.CreateAPIView):
    """Получение токена по никнейму и коду подтверждения."""

    serializer_class = TokenCreationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        print(request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.save()
        return Response(token_data)

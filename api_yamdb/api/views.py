from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import IsAuthorOrReadOnly
from api.serializers import CommentSerializer, ReviewsSerializer
from reviews.models import Review, Title


class ReviewsViewSet(viewsets.ModelViewSet):
    """Управление отзывами на произведения."""
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

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
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

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

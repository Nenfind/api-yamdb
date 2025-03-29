from rest_framework import filters, mixins, viewsets

from api.permissions import IsAdminOrReadOnly


class CategoryGenreViewSetBase(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet,
):
    """Основа для вьюсетов категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

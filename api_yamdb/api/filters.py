"""Фильтры для произведений."""
import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр произведений по жанрам, категориям и другим полям."""
    id = django_filters.NumberFilter(field_name='id')
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')
    name = django_filters.CharFilter(lookup_expr='icontains')
    year = django_filters.NumberFilter()

    class Meta:
        """Мета-класс для фильтра."""
        model = Title
        fields = ('genre', 'category', 'name', 'year')

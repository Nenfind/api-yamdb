from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentsViewSet,
    GenreViewSet,
    ReviewsViewSet,
    TitleViewSet,
    TokenObtainView,
    UserCreateAPIView,
    UserViewSet
)

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments')

router_v1.register(
    'users',
    UserViewSet,
    basename='users'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', UserCreateAPIView.as_view(), name='create'),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token'),
]

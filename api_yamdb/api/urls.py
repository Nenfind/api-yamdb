from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CommentsViewSet, ReviewsViewSet

router_v1 = DefaultRouter()
router_v1.register(
    r'titles/(?P<title_id>[\w.@+-]+)/reviews/(?P<review_id>[\w.@+-]+)',
    ReviewsViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>[\w.@+-]+)/reviews/(?P<review_id>[\w.@+-]+)/comments/(?P<comment_id>[\w.@+-]+)',
    CommentsViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]

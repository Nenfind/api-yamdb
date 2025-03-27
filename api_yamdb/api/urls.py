from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserCreateAPIView, TokenObtainView

router_v1 = DefaultRouter()
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

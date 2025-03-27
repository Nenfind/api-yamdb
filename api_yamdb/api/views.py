from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from rest_framework import viewsets, generics, permissions, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from .serializers import UserSerializer, TokenCreationSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        send_mail(
            subject='Код подтверждения YaMDB',
            message=f'Привет, {user.username}!\n\n'
                    f'Ваш код подтверждения: {user.secret}\n\n'
                    f'Используйте его для входа в систему.',
            from_email='yamdb@ya.ru',
            recipient_list=[user.email],
            fail_silently=True,
        )

class TokenObtainView(generics.CreateAPIView):
    serializer_class = TokenCreationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.save()
        return Response(token_data)

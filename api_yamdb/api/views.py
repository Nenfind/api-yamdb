from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics, permissions, mixins, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from .serializers import AdminUserSerializer, TokenCreationSerializer, PublicUserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer


class UserCreateAPIView(generics.CreateAPIView):
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
    serializer_class = TokenCreationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.save()
        return Response(token_data)

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким никнеймом уже существует.'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Этот электронный адрес уже занят.'
            )
        return value


class PublicUserSerializer(AdminUserSerializer):

    class Meta(AdminUserSerializer.Meta):
        fields = ('username', 'email')


class TokenCreationSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise AuthenticationFailed("Неправильный код подтверждения.")
        return data

    def create(self, validated_data):
        user = get_object_or_404(User, username=validated_data['username'])
        refresh = RefreshToken.for_user(user)
        return {'token': str(refresh.access_token)}

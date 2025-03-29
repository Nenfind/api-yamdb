import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_username(username):
    """
    Проверяет username на:
    1. Запрещённые символы (выводит их список в ошибке).
    2. Запрет имени 'me'.
    """

    if username.lower() == 'me':
        raise ValidationError(
            'Нельзя создать пользователя с никнеймом me!'
        )

    pattern = r'^[\w.@+-]+\Z'
    if not re.fullmatch(pattern, username):
        invalid_chars = re.sub(r'[\w.@+-]', '', username)
        raise ValidationError(
            f'Недопустимые символы в имени: {invalid_chars}. '
            'Можно использовать только буквы, цифры, и символы @/./+/-/_.'
        )


def validate_year(value):
    """Проверяет, что год не превышает текущий."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год не может быть больше текущего ({current_year})'
        )

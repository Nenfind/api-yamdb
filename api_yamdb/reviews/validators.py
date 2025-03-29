import re

from django.core.exceptions import ValidationError


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

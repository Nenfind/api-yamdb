from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Comment, Review, Title

User = get_user_model()


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Модель админки для произведений."""

    list_display = (
        'id',
        'name',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Модель админки для комментариев"""

    list_display = (
        'id',
        'review',
        'text',
        'author',
        'pub_date',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Модель админки для отзывов."""

    list_display = (
        'id',
        'title',
        'text',
        'author',
        'score',
        'pub_date',
    )


class YamdbUserAdmin(UserAdmin):
    """Модель админки для управления пользователями"""

    model = User
    fieldset = ['bio', 'role', 'username', 'email', 'first_name', 'last_name']


admin.site.register(User, YamdbUserAdmin)

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администраторам."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает создание/изменение/удаление только администраторам."""
    """Всем остальным - только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsOwnerAdminModeratorOrReadOnly(permissions.BasePermission):
    """
    Разрешает изменение/удаление только владельцу, модератору или админу.
    Всем остальным - только чтение.
    Создавать могут аутентифицированные пользователи.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            obj.author == request.user
            or request.user.is_moderator
        )

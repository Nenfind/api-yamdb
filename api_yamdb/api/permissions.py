from rest_framework import permissions


class AdminOrOwnerOrReadOnly(permissions.BasePermission):
    """Запрещает изменения всем, кроме администратора и владельца объекта."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.Role.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администраторам."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == request.user.Role.ADMIN)

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and
                request.user.role == request.user.Role.ADMIN)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает создание/изменение/удаление только администраторам."""
    """Всем остальным - только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
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
            or request.user.role in (
                request.user.Role.ADMIN,
                request.user.Role.MODERATOR
            )
        )

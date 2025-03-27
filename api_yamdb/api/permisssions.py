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

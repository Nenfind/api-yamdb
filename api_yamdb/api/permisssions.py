from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Permits for owners of an object to modify it."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.Role.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)

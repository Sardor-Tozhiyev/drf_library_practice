from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Reading is allowed to authenticated users; writing is restricted to staff."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff

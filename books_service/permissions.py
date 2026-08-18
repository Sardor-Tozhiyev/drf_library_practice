from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    """Reading is allowed for all authenticated users; writing is restricted to staff only."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

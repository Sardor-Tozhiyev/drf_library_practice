from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Читання (GET, HEAD, OPTIONS) доступне всім.
    Створення/редагування/видалення — лише staff (адміністратор бібліотеки).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

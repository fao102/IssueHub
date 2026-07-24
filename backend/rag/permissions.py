from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """Any authenticated user can read; only staff can create/update/destroy.

    Knowledge articles are curated by support staff, so writes are staff-only
    (unlike ticket categories, which any authenticated user may create).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

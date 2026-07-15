from rest_framework import permissions


class IsStaffOrReadCreateOnly(permissions.BasePermission):
    """Any authenticated user can list/create; only staff can update/destroy."""

    staff_only_actions = {"update", "partial_update", "destroy"}

    def has_permission(self, request, view):
        if getattr(view, "action", None) in self.staff_only_actions:
            return bool(request.user and request.user.is_staff)
        return True

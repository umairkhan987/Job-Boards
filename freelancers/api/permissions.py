from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsValidUser(BasePermission):
    message = "You are not permitted to perform this action."

    def has_permission(self, request, view):
        if request.user.is_Freelancer:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
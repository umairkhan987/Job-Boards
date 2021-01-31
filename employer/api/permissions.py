from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsEmployer(BasePermission):
    message = "Please login as Employer."

    def has_permission(self, request, view):
        if request.user.is_Employer:
            return True


class IsValidUser(BasePermission):
    message = "You are not permitted to perform this action."

    def has_permission(self, request, view):
        if request.user.is_Employer:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
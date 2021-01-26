from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsFreelancer(BasePermission):
    message = "Please login as freelancer."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_Freelancer:
            return True
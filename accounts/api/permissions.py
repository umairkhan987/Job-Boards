from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsFreelancer(BasePermission):
    message = "Please login as freelancer."

    def has_permission(self, request, view):
        if request.user.is_Freelancer:
            return True
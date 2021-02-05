from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsFreelancer
from .serializers import UserSerializer, MyTokenObtainPairSerializer, ChangePasswordSerializer, UpdateAccountSerializer, \
    UpdateProfileSerializer
from ..decorators import freelancer_required
from ..models import User, Profile


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def register(request, *args, **kwargs):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=201)


class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        return self.request.user


class UpdateAccountView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateAccountSerializer

    def get_object(self, queryset=None):
        return self.request.user


class UpdateProfileView(UpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated, IsFreelancer)
    serializer_class = UpdateProfileSerializer

    def get_object(self, queryset=None):
        return self.request.user.profile


# Deprecated
@api_view(['PUT'])
@permission_classes([IsAuthenticated, ])
def update_profile_view(request, *args, **kwargs):
    if not request.user.is_Freelancer:
        return Response({"detail": "Please login as freelancer."})
    else:
        profile = request.user.profile
        serializer = UpdateProfileSerializer(instance=profile, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)

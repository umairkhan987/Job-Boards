from rest_framework import serializers

from accounts.models import Profile, User
from employer.models import PostTask


class PostTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTask
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "profileImg", "email"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"
        depth = 1

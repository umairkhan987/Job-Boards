from rest_framework import serializers

from accounts.models import Profile, User
from employer.models import PostTask
from freelancers.models import Proposal


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTask
        fields = "__all__"


class SimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["rating", ]


class UserSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "profileImg", "email", "rating"]

    def get_rating(self, instance):
        return instance.profile.rating


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"
        depth = 1


class ProposalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = ("id", "rate", "days", "created_at", "updated_at", "user")


class WorkHistoryProposalSerializer(serializers.ModelSerializer):
    task_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proposal
        fields = ("id", "rating", "onBudget", "onTime", "comment", "created_at", "updated_at", "task_title")

    def get_task_title(self, instance):
        return instance.task.title


class BookmarkedSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class ProfileBookmarkSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    profileImg = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ("name", "tags", "id", "rating", "profileImg")

    def get_name(self, instance):
        return instance.user.first_name + " " + instance.user.last_name

    def get_profileImg(self, instance):
        if instance.user.profileImg:
            return instance.user.profileImg.url
        else:
            return None


class TaskBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTask
        fields = ("id", "title", "project_type", "no_of_days", "exp_level")

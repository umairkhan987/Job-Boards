from rest_framework import serializers

from employer.models import Offers
from freelancers.models import Proposal
from notification.models import Notification


class ProposalSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(required=True, write_only=True)
    title = serializers.SerializerMethodField(read_only=True)
    project_type = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proposal
        fields = ("task_id", "rate", "days", "title", "project_type", "status")

    def validate_days(self, value):
        if value < 1:
            raise serializers.ValidationError({"days": "Days is greater then 1"})
        return value

    def validate_rate(self, value):
        if value < 1:
            raise serializers.ValidationError({"rate": "Rate is greater then 0"})
        return value

    def get_title(self, instance):
        return instance.task.title

    def get_project_type(self, instance):
        return instance.task.project_type

    def get_status(self, instance):
        if instance.status:
            return instance.status
        else:
            return "Pending"


class OfferSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    profile_pic = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offers
        exclude = ("profile", "sender")

    def get_name(self, instance):
        return instance.sender.first_name + " " + instance.sender.last_name

    def get_email(self, instance):
        return instance.sender.email

    def get_profile_pic(self, instance):
        if instance.sender.profileImg:
            return instance.sender.profileImg.url
        else:
            return None


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proposal
        exclude = ("user", "rate", "days", "status", "task")

    def get_title(self, instance):
        return instance.task.title


class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField(read_only=True)
    action_desc = serializers.SerializerMethodField(read_only=True)
    target_title = serializers.SerializerMethodField(read_only=True)
    target_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "is_seen", "timestamp", "actor_name", "action_desc", "target_title", "target_url")

    def get_actor_name(self, instance):
        return instance.get_actor_full_name()

    def get_action_desc(self, instance):
        return instance.get_action_display()

    def get_target_title(self, instance):
        if instance.compare_action():
            return str(instance.target)
        else:
            return None

    def get_target_url(self, instance):
        if instance.compare_action():
            return instance.get_absolute_url()
        else:
            return None

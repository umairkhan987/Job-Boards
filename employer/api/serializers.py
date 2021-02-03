from rest_framework import serializers

from employer.models import PostTask, Offers
from freelancers.models import Proposal
from hireo.api.serializers import ProposalSerializer, UserSerializer
from notification.models import Notification


class PostTaskSerializer(serializers.ModelSerializer):
    skills = serializers.ListField()

    class Meta:
        model = PostTask
        exclude = ('user', 'created_at', 'updated_at', 'job_status')

    def validate(self, attrs):
        if attrs['min_price'] >= attrs['max_price']:
            raise serializers.ValidationError({"min_price": "Min price is less than Max price"})
        return attrs


class ProposalListSerializer(ProposalSerializer):
    title = serializers.SerializerMethodField(read_only=True)

    class Meta(ProposalSerializer.Meta):
        fields = ProposalSerializer.Meta.fields + ("title", "status", "rating", "comment",)

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
            return instance.target.title
        else:
            return None

    def get_target_url(self, instance):
        if instance.compare_action():
            return instance.get_absolute_url()
        else:
            return None


class ReviewProposalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    # comment = serializers.CharField(required=True, max_length=1000),

    class Meta:
        model = Proposal
        fields = "__all__"

    def validate(self, attrs):
        if not attrs.get("comment", None):
            raise serializers.ValidationError({"comment": "This field is required"})
        return attrs


class OfferSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(required=True)

    class Meta:
        model = Offers
        fields = ("profile_id", "offer_message", "offer_file")

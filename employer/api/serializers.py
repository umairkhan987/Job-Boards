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
    class Meta:
        model = Notification
        fields = "__all__"


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
    class Meta:
        model = Offers
        fields = "__all__"

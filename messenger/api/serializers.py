from rest_framework import serializers

from messenger.models import Messages


class MessageSerializer(serializers.ModelSerializer):
    receiver_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = Messages
        fields = ("receiver_id", "message_content", "created_at")


class MessageDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Messages
        exclude = ("message_not_visible_to", )


class InboxUserListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField(read_only=True)
    sender_img = serializers.SerializerMethodField(read_only=True)
    receiver_name = serializers.SerializerMethodField(read_only=True)
    receiver_img = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Messages
        exclude = ("message_not_visible_to", "is_read")

    def get_sender_name(self, instance):
        return instance.sender.get_full_name()

    def get_receiver_name(self, instance):
        return instance.receiver.get_full_name()

    def get_receiver_img(self, instance):
        return instance.receiver.get_profile_image_url()

    def get_sender_img(self, instance):
        return instance.sender.get_profile_image_url()

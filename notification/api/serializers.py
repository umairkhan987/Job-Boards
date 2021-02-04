from rest_framework import serializers

from notification.models import MessageNotification


class MessageNotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField(read_only=True)
    profileImg = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MessageNotification
        fields = "__all__"

    def get_sender_name(self, instance):
        return instance.actor.first_name + " " + instance.actor.last_name

    def get_profileImg(self, instance):
        if instance.actor.profileImg:
            return instance.actor.profileImg.url
        else:
            return None

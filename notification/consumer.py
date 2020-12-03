from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationsConsumer(AsyncJsonWebsocketConsumer):

    async def websocket_connect(self, event):
        # print("CONNECTED ", event)
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def websocket_disconnect(self, event):
        # print("DISCONNECTED ", event)
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def websocket_receive(self, event):
        # print("RECEIVE", event)
        if event['key'] == "user_notification":
            context = await self.get_notification_info(self.scope)
            await self.send_json(content=context)
        if event["key"] == "msg_notification":
            context = await self.get_msg_notification_info(self.scope)
            await self.send_json(content=context)

    @database_sync_to_async
    def get_notification_info(self, scope):
        context = None
        if scope['user'].is_authenticated:
            context = {
                "unread_notification_count": scope['user'].notifications.filter(is_seen=False).count(),
                "type": "user"
            }
        return context

    @database_sync_to_async
    def get_msg_notification_info(self, scope):
        context = None
        if scope["user"].is_authenticated:
            context = {
                "unread_msg_notification_count": scope["user"].msg_notifications.filter(is_seen=False).count(),
                "type": "message",
            }
        return context

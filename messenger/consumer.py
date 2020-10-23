from channels.generic.websocket import AsyncJsonWebsocketConsumer


class MessengerConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        # print("CONNECTED ", event)
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(f"{self.scope['user'].id}", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def websocket_disconnect(self, event):
        # print("DISCONNECTED ", event)
        await self.channel_layer.group_discard(f"{self.scope['user'].id}", self.channel_name)

    async def websocket_receive(self, event):
        # print("RECEIVED ", event)
        await self.send_json(event)

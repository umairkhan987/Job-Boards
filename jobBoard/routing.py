from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.urls import path

from notification.consumer import NotificationsConsumer
from messenger.consumer import MessengerConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('notifications/', NotificationsConsumer.as_asgi()),
                    path("<int:user_id>/", MessengerConsumer.as_asgi()),
                ]
            )
        )
    )
})

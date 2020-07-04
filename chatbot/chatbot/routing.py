from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from .consumers import NotificationConsumer  # Importing notification Consumer from consumers.py


# application = ProtocolTypeRouter({ 
#     # Websocket chat handler
#     'websocket': AllowedHostsOriginValidator(  # Only allow socket connections from the Allowed hosts in the settings.py file
#         AuthMiddlewareStack(  # Session Authentication, required to use if we want to access the user details in the consumer 
#             URLRouter(
#                 [
#                     path("notifications/", NotificationConsumer),    # Url path for connecting to the websocket to send notifications.
#                 ]
#             )
#         ),
#     ),
# })

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                    path("notifications/", NotificationConsumer),    # Url path for connecting to the websocket to send notifications.
                ]
        )
    ),
})
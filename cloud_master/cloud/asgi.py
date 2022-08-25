import os

from bson import ObjectId
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

import cloud_ws.routing
from vendor.django_mongoengine.mongo_auth.models import MongoUser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloud.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()
MongoUser._meta.pk.to_python = ObjectId

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                cloud_ws.routing.websocket_urlpatterns,
            )
        )
    ),
})

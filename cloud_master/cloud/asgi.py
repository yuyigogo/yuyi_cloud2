"""
ASGI config for cloud project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloud.settings")

application = get_asgi_application()

# import os
#
# from channels.routing import ProtocolTypeRouter
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     # Just HTTP for now. (We can add other protocols later.)
# })
# import os
#
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud.settings')
#
# django_application = get_asgi_application()
#
#
# async def application(scope, receive, send):
#     if scope['type'] == 'http':
#         # Let Django handle HTTP requests
#         await django_application(scope, receive, send)
#     elif scope['type'] == 'websocket':
#         # We'll handle Websocket connections here
#         pass
#     else:
#         raise NotImplementedError(f"Unknown scope type {scope['type']}")

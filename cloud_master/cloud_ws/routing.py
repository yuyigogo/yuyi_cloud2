# this file is url routing for websocket
from django.urls import re_path

from . import sensor_list_consumers

websocket_urlpatterns = [
    re_path(
        r"ws/sensor_list/sensor_type/(?P<sensor_type>\w+)/sensor_id/(?P<sensor_id>[a-zA-Z0-9]+)/$",
        sensor_list_consumers.SensorListConsumer.as_asgi(),
    ),
]

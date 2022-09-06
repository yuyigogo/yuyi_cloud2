from django.urls import path, re_path
from equipment_management.apis.gateway_apis import (
    GatewaysView,
    GatewayView,
    SiteGatewaysView,
)
from equipment_management.apis.pub_sensor_config_apis import SensorConfigView

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/gateways/$",
        SiteGatewaysView.as_view(),
        name="gateways_in_site",
    ),
    re_path(
        r"^gateways/$",
        GatewaysView.as_view(),
        name="gateways_actions",
    ),
    re_path(
        r"^gateways/(?P<gateway_id>[a-zA-Z0-9]+)/$",
        GatewayView.as_view(),
        name="gateway_actions",
    ),
    re_path(
        r"^gateway/(?P<client_number>[a-zA-Z0-9]+)/sensor_id/(?P<sensor_id>[a-zA-Z0-9]+)/$",
        SensorConfigView.as_view(),
        name="sensor_config_actions",
    ),
]

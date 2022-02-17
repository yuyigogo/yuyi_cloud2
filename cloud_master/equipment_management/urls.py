from django.urls import path, re_path
from equipment_management.apis.gateway_apis import (
    GatewaysView,
    GatewayView,
    SiteGatewaysView,
)

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/gateways/$",
        SiteGatewaysView.as_view(),
        name="gateways_in_site",
    ),
    re_path(r"^gateways/$", GatewaysView.as_view(), name="gateways_actions",),
    re_path(
        r"^gateways/(?P<gateway_id>[a-zA-Z0-9]+)/$",
        GatewayView.as_view(),
        name="gateway_actions",
    ),
]

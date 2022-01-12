from django.urls import re_path

from equipment_management.apis.gateway_apis import GatewaySensorsView, SensorsByPublishView
from sites.apis.site_apis import CustomerSitesView, CustomerSiteView

urlpatterns = [
    re_path(
        r"^customer_sites/(?P<customer_id>[a-zA-Z0-9]+)/$",
        CustomerSitesView.as_view(),
        name="customer_sits",
    ),
    re_path(
        r"^customer/(?P<customer_id>[a-zA-Z0-9]+)/sites/(?P<site_id>[a-zA-Z0-9]+)/$",
        CustomerSiteView.as_view(),
        name="site_actions",
    ),
    re_path(
        r"^gateways/(?P<client_number>[a-zA-Z0-9]+)/sensor_info/$",
        GatewaySensorsView.as_view(),
        name="sensor_info_in_gateway",
    ),
    re_path(
        r"^gateways/(?P<client_number>[a-zA-Z0-9]+)/sensors/$",
        SensorsByPublishView.as_view(),
        name="sensors_by_publish",
    ),
]

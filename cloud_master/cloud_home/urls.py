from cloud_home.apis.asset_count_apis import CustomerAssetsView, SiteAssetsView
from django.urls import path, re_path

from cloud_home.apis.latest3_alarms import LatestAlarmsView
from cloud_home.apis.map_apis import MapTressView
from cloud_home.apis.site_equipment_status import EquipmentsStatusView, SitesStatusView

urlpatterns = [
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/assets/$",
        CustomerAssetsView.as_view(),
        name="customer_assets",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/assets/$",
        SiteAssetsView.as_view(),
        name="site_assets",
    ),
    path("map/customer-tress/", MapTressView.as_view(), name="map_tress"),
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/site-status/$",
        SitesStatusView.as_view(),
        name="site_status",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/equipment-status/$",
        EquipmentsStatusView.as_view(),
        name="equipment_status",
    ),
    path("latest/alarms/", LatestAlarmsView.as_view(), name="latest3_alarms"),
]

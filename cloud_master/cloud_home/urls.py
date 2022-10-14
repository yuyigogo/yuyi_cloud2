from cloud_home.apis.abnormal_count_apis import (
    CustomerAbnormalCountView,
    SiteAbnormalCountView,
)
from cloud_home.apis.abnormal_ratio_apis import (
    CustomerAbnormalRatioView,
    SiteAbnormalRatioView,
)
from cloud_home.apis.latest3_alarms import LatestAlarmsView
from cloud_home.apis.map_apis import MapTressView
from cloud_home.apis.status_statistics_apis import CustomerStatusView, SiteStatusView
from django.urls import path, re_path

urlpatterns = [
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/status-infos/$",
        CustomerStatusView.as_view(),
        name="customer_status_info",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/status-infos/$",
        SiteStatusView.as_view(),
        name="site_status_info",
    ),
    path("map/customer-tress/", MapTressView.as_view(), name="map_tress"),
    path("latest/alarms/", LatestAlarmsView.as_view(), name="latest3_alarms"),
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/abnormal-ratio/$",
        CustomerAbnormalRatioView.as_view(),
        name="customer_abnormal_ratio",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/abnormal-ratio/$",
        SiteAbnormalRatioView.as_view(),
        name="site_abnormal_ratio",
    ),
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/count-abnormal/$",
        CustomerAbnormalCountView.as_view(),
        name="customer_abnormal_count",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/count-abnormal/$",
        SiteAbnormalCountView.as_view(),
        name="site_abnormal_count",
    ),
]

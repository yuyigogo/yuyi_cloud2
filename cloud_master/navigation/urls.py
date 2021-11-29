from django.urls import path, re_path
from navigation.apis.equipment_navigation_apis import (
    CustomerSensorsView,
    CustomerTreesView,
    EquipmentSensorsView,
    SiteSensorsView,
)
from navigation.apis.gateway_navigation_apis import GatewayTreesView
from navigation.apis.points_trend_apis import PointsTrendView
from navigation.apis.sensor_apis import SensorDetailsView

urlpatterns = [
    re_path(
        r"^equipments/(?P<equipment_id>[a-zA-Z0-9]+)/sensor_info/$",
        EquipmentSensorsView.as_view(),
        name="sensor_info_in_equipment",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/sensor_info/$",
        SiteSensorsView.as_view(),
        name="sensor_info_in_site",
    ),
    # re_path(
    #     r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/sensor_info/$",
    #     CustomerSensorsView.as_view(),
    #     name="sensor_info_in_customer",
    # ),
    path("customer-trees/", CustomerTreesView.as_view(), name="customer_trees_info"),
    path("gateway-trees/", GatewayTreesView.as_view(), name="customer_gateway_trees_info"),
    re_path(r"^points_trend/$", PointsTrendView.as_view(), name="points_trend"),
    re_path(
        r"^sensor/(?P<pk>[a-zA-Z0-9]+)/details/$",
        SensorDetailsView.as_view(),
        name="sensor_details",
    ),
]

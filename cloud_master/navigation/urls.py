from django.urls import path, re_path
from navigation.apis.equipment_navigation_apis import (
    CustomerSensorsView,
    CustomerTreesView,
    EquipmentSensorsView,
    SiteSensorsView,
)

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/equipments/(?P<equipment_id>[a-zA-Z0-9]+)/sensor_info/$",
        EquipmentSensorsView.as_view(),
        name="sensor_info_in_equipment",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/sensor_info/$",
        SiteSensorsView.as_view(),
        name="sensor_info_in_site",
    ),
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/sensor_info/$",
        CustomerSensorsView.as_view(),
        name="sensor_info_in_customer",
    ),
    path("customer-trees/", CustomerTreesView.as_view(), name="customer_trees_info",),
]

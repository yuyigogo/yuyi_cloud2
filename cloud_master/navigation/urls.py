from django.urls import re_path

from navigation.apis.equipment_navigation_apis import (
    EquipmentNavigationView,
    EquipmentsNavigationView,
)

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/equipments/(?P<equipment_id>[a-zA-Z0-9]+)/sensor_info/$",
        EquipmentNavigationView.as_view(),
        name="sensor_info_in_equipment",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/sensor_info/$",
        EquipmentsNavigationView.as_view(),
        name="sensor_info_in_site",
    ),
]

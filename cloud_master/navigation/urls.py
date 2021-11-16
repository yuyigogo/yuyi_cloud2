from django.urls import re_path

from navigation.apis.equipment_navigation_apis import EquipmentNavigationView

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/equipments/(?P<equipment_id>[a-zA-Z0-9]+)/$",
        EquipmentNavigationView.as_view(),
        name="sensor_info_in_equipment",
    ),
]

from alarm_management.apis.alarm_apis import EquipmentAlarmListView, SiteAlarmListView
from django.urls import re_path

urlpatterns = [
    re_path(
        r"^equipments/(?P<equipment_id>[a-zA-Z0-9]+)/alarm_info/$",
        EquipmentAlarmListView.as_view(),
        name="sensor_info_in_equipment",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/alarm_info/$",
        SiteAlarmListView.as_view(),
        name="sensor_info_in_site",
    ),
]

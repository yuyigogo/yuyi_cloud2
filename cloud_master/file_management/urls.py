from django.urls import re_path

from file_management.apis.equipment_apis import EquipmentListView
from file_management.apis.measure_point_apis import MeasurePointListView

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/equipment/$",
        EquipmentListView.as_view(),
        name="equipments_actions",
    ),
    re_path(
        r"^equipment/(?P<equipment_id>[a-zA-Z0-9]+)/point/$",
        MeasurePointListView.as_view(),
        name="measure_point_actions",
    ),
]

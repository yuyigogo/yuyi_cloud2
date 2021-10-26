from django.urls import re_path

from equipment_management.equipment_apis import EquipmentListView

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/equipment/$",
        EquipmentListView.as_view(),
        name="equipments_actions",
    ),
]

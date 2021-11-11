from django.urls import path, re_path
from file_management.apis.equipment_apis import EquipmentListView
from file_management.apis.file_navigation_apis import (
    AllFileNavigationTreeView,
    FileNavigationTreeView,
)
from file_management.apis.measure_point_apis import (
    MeasurePointListView,
    MeasurePointView,
)

urlpatterns = [
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/equipment/$",
        EquipmentListView.as_view(),
        name="equipments_actions",
    ),
    re_path(
        r"^equipment/(?P<equipment_id>[a-zA-Z0-9]+)/point/$",
        MeasurePointListView.as_view(),
        name="measure_points_actions",
    ),
    re_path(
        r"^equipment/(?P<equipment_id>[a-zA-Z0-9]+)/point/(?P<point_id>[a-zA-Z0-9]+)/$",
        MeasurePointView.as_view(),
        name="measure_point_actions",
    ),
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/file_tree/$",
        FileNavigationTreeView.as_view(),
        name="customer_file_tree",
    ),
    re_path(
        r"^all_customers/file_tree/$",
        AllFileNavigationTreeView.as_view(),
        name="all_customer_file_tree",
    ),
]

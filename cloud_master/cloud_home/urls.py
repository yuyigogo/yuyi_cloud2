from cloud_home.apis.asset_count_apis import CustomerAssetsView
from django.urls import path, re_path

urlpatterns = [
    re_path(
        r"^customers/(?P<pk>[a-zA-Z0-9]+)/assets/$",
        CustomerAssetsView.as_view(),
        name="customer_assets",
    ),
]

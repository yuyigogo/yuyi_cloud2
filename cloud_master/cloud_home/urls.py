from cloud_home.apis.asset_count_apis import CustomerAssetsView, SiteAssetsView
from django.urls import path, re_path

urlpatterns = [
    re_path(
        r"^customers/(?P<customer_id>[a-zA-Z0-9]+)/assets/$",
        CustomerAssetsView.as_view(),
        name="customer_assets",
    ),
    re_path(
        r"^sites/(?P<site_id>[a-zA-Z0-9]+)/assets/$",
        SiteAssetsView.as_view(),
        name="site_assets",
    ),
]

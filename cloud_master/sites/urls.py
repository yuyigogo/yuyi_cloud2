from django.urls import re_path
from sites.apis.site_apis import CustomerSitesView, CustomerSiteView

urlpatterns = [
    re_path(
        r"^customer_sites/(?P<customer_id>[a-zA-Z0-9]+)/$",
        CustomerSitesView.as_view(),
        name="customer_sits",
    ),
    re_path(
        r"^customer/(?P<customer_id>[a-zA-Z0-9]+)/sites/(?P<site_id>[a-zA-Z0-9]+)/$",
        CustomerSiteView.as_view(),
        name="site_actions",
    ),
]

from customer.apis.customer_apis import CustomersView, CustomerView
from django.urls import path, re_path

urlpatterns = [
    path("customers/", CustomersView.as_view(), name="customers_actions"),
    re_path(
        r"^customers/(?P<pk>[a-zA-Z0-9]+)/$",
        CustomerView.as_view(),
        name="customer_actions",
    ),
]

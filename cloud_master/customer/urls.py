from django.urls import path

from customer.apis.customer_apis import CustomersView

urlpatterns = [
    path("customers/", CustomersView.as_view(), name="customers_actions"),
]

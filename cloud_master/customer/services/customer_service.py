from typing import Optional

from common.const import ALL
from customer.models.customer import Customer
from sites.models.site import Site
from user_management.models.user import CloudUser

from common.framework.service import BaseService


class CustomerService(BaseService):
    @classmethod
    def create_customer(
        cls, name: str, administrative_division: str, remarks: Optional[str] = None
    ) -> Customer:
        customer = Customer(
            name=name, administrative_division=administrative_division, remarks=remarks
        )
        customer.save()
        return customer

    @classmethod
    def delete_customer(cls, customer: Customer):
        # when delete customer, will delete the resources in this customer
        Site.objects.filter(customer=customer.pk).delete()
        CloudUser.filter(customer=customer.pk).delete()
        customer.delete()

    @classmethod
    def named_all_customer(cls):
        return Customer.objects.get(name=ALL)

from typing import Optional

from customer.models.customer import Customer

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

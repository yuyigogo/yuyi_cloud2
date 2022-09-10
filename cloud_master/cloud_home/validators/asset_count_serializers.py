from customer.models.customer import Customer
from mongoengine import DoesNotExist

from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer


class CustomerAssetSerializer(BaseSerializer):
    def validate(self, data):
        customer_id = self.context["customer_id"]
        try:
            customer = Customer.objects.get(pk=customer_id)
        except DoesNotExist:
            raise APIException(f"invalid {customer_id=}")
        data["customer"] = customer
        return data

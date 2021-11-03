from mongoengine import DoesNotExist

from common.const import ALL
from common.framework.exception import APIException, ForbiddenException
from common.framework.serializer import BaseSerializer
from customer.models.customer import Customer


class FileTreeSerializer(BaseSerializer):
    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        customer_id = self.context["customer_id"]
        try:
            customer = Customer.objects.get(id=customer_id)
        except DoesNotExist:
            raise APIException(f"invalid {customer_id=}")
        if not user.is_cloud_or_client_super_admin():
            if str(user.customer) != customer_id:
                raise ForbiddenException("user has no right to this customer!")
        is_all_customer = customer.name == ALL
        self.context["is_all_customer"] = is_all_customer
        self.context["customer"] = customer
        return data

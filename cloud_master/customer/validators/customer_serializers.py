from customer.models.customer import Customer
from rest_framework.fields import CharField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.error_code import StatusCode
from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer


class CustomerCreateSerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    administrative_division = CharField(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)

    def validate_name(self, name: str) -> str:
        if Customer.objects(name=name).count() > 0:
            raise APIException(
                "customer name duplicate!",
                code=StatusCode.CUSTOMER_NAME_DUPLICATE.value,
            )
        return name

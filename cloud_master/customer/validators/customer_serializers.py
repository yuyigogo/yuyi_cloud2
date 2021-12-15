from customer.models.customer import Customer
from mongoengine import DoesNotExist
from rest_framework.fields import CharField, BooleanField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.error_code import StatusCode
from common.framework.exception import APIException, ForbiddenException
from common.framework.serializer import BaseSerializer


class CustomerCreateSerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    administrative_division = CharField(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)

    def validate_name(self, name: str) -> str:
        if Customer.objects(name=name).count() > 0:
            raise APIException(
                "公司名称已存在!",
                code=StatusCode.CUSTOMER_NAME_DUPLICATE.value,
            )
        return name


class CustomerSerializer(BaseSerializer):
    def validate(self, data: dict) -> dict:
        customer_id = self.context["pk"]
        try:
            customer = Customer.objects.get(pk=customer_id)
        except DoesNotExist:
            raise APIException(f"invalid {customer_id=}")
        self.context["customer"] = customer
        return data


class DeleteCustomerSerializer(CustomerSerializer):
    clear_resource = BooleanField(default=False)

    def validate(self, data: dict) -> dict:
        data = super(DeleteCustomerSerializer, self).validate(data)
        user = self.context["request"].user
        customer_id = self.context["pk"]
        if str(user.customer) == customer_id:
            raise ForbiddenException("user can't update/delete own customer")
        return data


class UpdateCustomerSerializer(DeleteCustomerSerializer):
    name = CharField(max_length=MAX_LENGTH_NAME, required=False)
    administrative_division = CharField(required=False)
    remarks = CharField(required=False)

    def validate(self, data: dict) -> dict:
        data = super(UpdateCustomerSerializer, self).validate(data)
        name = data.get("name")
        if name and Customer.objects.filter(name=name).count():
            raise APIException(
                "公司名称已存在!",
                code=StatusCode.CUSTOMER_NAME_DUPLICATE.value,
            )
        return data

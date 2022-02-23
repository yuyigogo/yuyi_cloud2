from customer.models.customer import Customer
from mongoengine import DoesNotExist
from rest_framework.fields import BooleanField, CharField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.error_code import StatusCode
from common.framework.exception import APIException, ForbiddenException
from common.framework.serializer import AdministrativeDivisionSerializer, BaseSerializer


class CustomerCreateSerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    administrative_division = AdministrativeDivisionSerializer()
    remarks = CharField(
        max_length=MAX_MESSAGE_LENGTH, required=False, allow_null=True, allow_blank=True
    )

    def validate_name(self, name: str) -> str:
        if Customer.objects(name=name).count() > 0:
            raise APIException(
                "公司名称已存在!", code=StatusCode.CUSTOMER_NAME_DUPLICATE.value,
            )
        return name


def valid_customer_id(customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
    except DoesNotExist:
        raise APIException(f"invalid {customer_id=}")
    return customer


class CustomerSerializer(BaseSerializer):
    def validate(self, data: dict) -> dict:
        customer_id = self.context["pk"]
        customer = valid_customer_id(customer_id)
        data["customer"] = customer
        return data


class DeleteCustomerSerializer(BaseSerializer):
    clear_resource = BooleanField(default=False)

    def validate(self, data: dict) -> dict:
        customer_id = self.context["pk"]
        customer = valid_customer_id(customer_id)
        data["customer"] = customer
        user = self.context["request"].user
        if str(user.customer) == customer_id:
            raise ForbiddenException("user can't update/delete own customer")
        return data


class UpdateCustomerSerializer(BaseSerializer):
    name = CharField(max_length=MAX_LENGTH_NAME, required=False)
    administrative_division = AdministrativeDivisionSerializer(required=False)
    remarks = CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data: dict) -> dict:
        customer_id = self.context["pk"]
        customer = valid_customer_id(customer_id)
        data["customer"] = customer
        name = data.get("name")
        if name and name != customer.name:
            if Customer.objects.filter(name=name).count() > 0:
                raise APIException(
                    "公司名称已存在!", code=StatusCode.CUSTOMER_NAME_DUPLICATE.value,
                )
        return data

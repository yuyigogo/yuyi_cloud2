from rest_framework.fields import CharField, FileField

from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer


class GatewayImportSerializer(BaseSerializer):
    file = FileField(required=True, allow_empty_file=False)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        validate_customer_id = None
        if user.is_normal_admin():
            validate_customer_id = user.customer
        data["validate_customer_id"] = validate_customer_id
        return data


class GatewayExportSerializer(BaseSerializer):
    customer_id = CharField(required=True)
    site_id = CharField(required=False)

    def validate(self, data: dict) -> dict:
        user = self.context["request"].user
        customer_id = data["customer_id"]
        if user.is_normal_admin() and str(user.customer) != customer_id:
            raise APIException(f"Not enough permission for this {customer_id=}")
        return data

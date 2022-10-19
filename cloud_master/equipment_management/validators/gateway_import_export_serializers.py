from rest_framework.fields import FileField

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

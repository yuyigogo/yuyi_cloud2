from rest_framework.fields import CharField, IntegerField, ListField
from sites.models.site import Site

from common.const import ALL, MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.error_code import StatusCode
from common.framework.exception import APIException, ForbiddenException
from common.framework.serializer import BaseSerializer


class GetCustomerSitesSerializer(BaseSerializer):
    def validate(self, data: dict) -> dict:
        customer_id = self.context["customer_id"]
        user = self.context["request"].user
        if user.is_cloud_or_client_super_admin():
            return data
        else:
            if str(user.customer_id) != customer_id:
                raise ForbiddenException(
                    "user can't get not belong to its own customer's sits"
                )
            return data


class CreateSiteSerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    administrative_division = CharField(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)
    voltage_level = IntegerField(required=True)
    site_location = ListField()

    def validate(self, data: dict) -> dict:
        name = data["name"]
        customer_id = self.context["customer_id"]
        if (
            name == ALL
            or Site.objects.filter(customer=customer_id, name=name).count() > 0
        ):
            raise APIException(
                "customer name duplicate!", code=StatusCode.SITE_NAME_DUPLICATE.value,
            )
        return data

from equipment_management.models.gateway import GateWay
from mongoengine import DoesNotExist
from rest_framework.fields import BooleanField, CharField, IntegerField
from sites.models.site import Site

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.error_code import StatusCode
from common.framework.exception import APIException, InvalidException
from common.framework.serializer import BaseSerializer


class CreateGatewaySerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    customer = CharField(required=True)
    client_number = CharField(required=True)
    time_adjusting = IntegerField(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)

    def validate_client_number(self, client_number):
        raise APIException(
            "该主机编号已绑定!", code=StatusCode.GATEWAY_DUPLICATE_CONFIGURED.value,
        )

    def validate(self, data: dict) -> dict:
        site_id = self.context["site_id"]
        try:
            site = Site.objects.get(id=site_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {site_id=}")
        if GateWay.objects.filter(site_id=site_id, name=data["name"]).count() > 0:
            raise APIException(
                "主机名称已存在!", code=StatusCode.GATEWAY_NAME_DUPLICATE.value,
            )
        return data


class UpdateGatewaySerializer(BaseSerializer):
    name = CharField(required=False, max_length=MAX_LENGTH_NAME)
    client_number = CharField(required=False)
    time_adjusting = IntegerField(required=False)
    remarks = CharField(required=False, max_length=MAX_MESSAGE_LENGTH)

    def validate(self, data: dict) -> dict:
        gateway_id = self.context["gateway_id"]
        try:
            gateway = GateWay.objects.get(pk=gateway_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {gateway_id=}")
        data["gateway"] = gateway
        name = data.get("name")
        client_number = data.get("client_number")
        if name and name != gateway.name:
            if GateWay.objects(site_id=gateway.site_id, name=name).count() > 0:
                raise APIException(
                    "主机名称已存在!", code=StatusCode.GATEWAY_NAME_DUPLICATE.value,
                )
        data["changed_client_id"] = False
        if client_number and client_number != gateway.client_number:
            if GateWay.objects(client_number=client_number).count() > 0:
                raise APIException(
                    "该主机编号已绑定!", code=StatusCode.GATEWAY_DUPLICATE_CONFIGURED.value,
                )
            data["changed_client_id"] = True
        return data


class DeleteGatewaySerializer(BaseSerializer):
    clear_resource = BooleanField(default=False)

    def validate(self, data):
        gateway_id = self.context["gateway_id"]
        try:
            gateway = GateWay.objects.get(pk=gateway_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {gateway_id=}")
        data["gateway"] = gateway
        return data

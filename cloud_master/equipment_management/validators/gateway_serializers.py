from customer.models.customer import Customer
from equipment_management.models.gateway import GateWay
from mongoengine import DoesNotExist
from rest_framework.fields import BooleanField, CharField, IntegerField
from sites.models.site import Site

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH, SensorType
from common.error_code import StatusCode
from common.framework.exception import APIException, InvalidException
from common.framework.serializer import BaseSerializer


def validate_site_id(site_id: str):
    try:
        site = Site.objects.get(id=site_id)
    except DoesNotExist:
        raise InvalidException(f"invalid {site_id=}")
    return site


class SiteGatewaysSerializer(BaseSerializer):
    def validate(self, data):
        site_id = self.context["site_id"]
        validate_site_id(site_id)
        return data


class CreateGatewaySerializer(BaseSerializer):
    name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    customer = CharField(required=True)
    site_id = CharField(required=True)
    client_number = CharField(required=True)
    time_adjusting = IntegerField(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH, required=False)

    def validate_customer(self, customer):
        try:
            Customer.objects.get(pk=customer)
        except DoesNotExist:
            raise APIException("公司不存在！")
        return customer

    def validate_site_id(self, site_id):
        try:
            Site.objects.get(pk=site_id)
        except DoesNotExist:
            raise APIException("站点不存在！")
        return site_id

    def validate_client_number(self, client_number):
        if GateWay.objects(client_number=client_number).count() > 0:
            raise APIException(
                "该主机编号已绑定!", code=StatusCode.GATEWAY_DUPLICATE_CONFIGURED.value,
            )
        return client_number

    def validate(self, data: dict) -> dict:
        if GateWay.objects.filter(name=data["name"]).count() > 0:
            raise APIException(
                "主机名称已存在!", code=StatusCode.GATEWAY_NAME_DUPLICATE.value,
            )
        return data


class UpdateGatewaySerializer(BaseSerializer):
    name = CharField(required=False, max_length=MAX_LENGTH_NAME)
    customer = CharField(required=False)
    site_id = CharField(required=False)
    client_number = CharField(required=False)
    time_adjusting = IntegerField(required=False)
    remarks = CharField(required=False, max_length=MAX_MESSAGE_LENGTH)

    def validate_customer(self, customer):
        try:
            Customer.objects.get(pk=customer)
        except DoesNotExist:
            raise APIException("公司不存在！")
        return customer

    def validate_site_id(self, site_id):
        try:
            Site.objects.get(pk=site_id)
        except DoesNotExist:
            raise APIException("站点不存在！")
        return site_id

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
            if GateWay.objects(name=name).count() > 0:
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


class SensorConfigSerializer(BaseSerializer):
    page = IntegerField(required=False)
    limit = IntegerField(required=False)
    sensor_name = CharField(required=False)
    sensor_id = CharField(required=False)
    sensor_type = CharField(required=False)

    def validate_sensor_type(self, sensor_type):
        if sensor_type not in SensorType.values():
            raise APIException(f"invalid sensor_type")
        return sensor_type

    def validate(self, data):
        gateway_id = self.context["gateway_id"]
        try:
            gateway = GateWay.objects.get(pk=gateway_id)
        except DoesNotExist:
            raise APIException(f"invalid gateway_id")
        data["gateway"] = gateway
        return data

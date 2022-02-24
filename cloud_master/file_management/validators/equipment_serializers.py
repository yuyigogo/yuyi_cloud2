from mongoengine import DoesNotExist
from rest_framework.fields import CharField, BooleanField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH, DeviceType, VoltageLevel
from common.error_code import StatusCode
from common.framework.exception import InvalidException, APIException
from common.framework.serializer import BaseSerializer
from file_management.models.electrical_equipment import ElectricalEquipment
from sites.models.site import Site


class CreateEquipmentSerializer(BaseSerializer):
    device_name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    device_type = CharField(required=True)
    voltage_level = CharField(required=True)
    operation_number = CharField()
    asset_number = CharField()
    device_model = CharField()
    factory_number = CharField()
    remarks = CharField(
        max_length=MAX_MESSAGE_LENGTH, allow_blank=True, allow_null=True
    )

    def validated_device_name(self, device_name):
        site_id = self.context["site_id"]
        if (
            ElectricalEquipment.objects(
                site_id=site_id, device_name=device_name
            ).count()
            > 0
        ):
            raise APIException(
                msg="电力设备名称已存在！", code=StatusCode.EQUIPMENT_NAME_DUPLICATE.value
            )
        return device_name

    def validated_device_type(self, device_type):
        if device_type not in DeviceType.values():
            raise APIException("非法的电力设备类型！")
        return device_type

    def validated_voltage_level(self, voltage_level):
        if voltage_level not in VoltageLevel.values():
            raise APIException("非法的电压等级！")
        return voltage_level

    def validate(self, data: dict) -> dict:
        site_id = self.context["site_id"]
        try:
            site = Site.objects.get(id=site_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {site_id=}")
        return data


class UpdateEquipmentSerializer(BaseSerializer):
    device_name = CharField(max_length=MAX_LENGTH_NAME)
    device_type = CharField()
    voltage_level = CharField()
    operation_number = CharField()
    asset_number = CharField()
    device_model = CharField()
    factory_number = CharField()
    remarks = CharField(
        max_length=MAX_MESSAGE_LENGTH, allow_blank=True, allow_null=True
    )

    def validate_device_name(self, device_name: str) -> str:
        site_id = self.context["site_id"]
        equipment_id = self.context["equipment_id"]
        if (
            ElectricalEquipment.objects(
                site_id=site_id, device_name=device_name, id__ne=equipment_id
            ).count()
            > 0
        ):
            raise APIException(
                msg="电力设备名称已存在！", code=StatusCode.EQUIPMENT_NAME_DUPLICATE.value
            )
        return device_name

    def validated_device_type(self, device_type):
        if device_type not in DeviceType.values():
            raise APIException("非法的电力设备类型！")
        return device_type

    def validated_voltage_level(self, voltage_level):
        if voltage_level not in VoltageLevel.values():
            raise APIException("非法的电压等级！")
        return voltage_level


class DeleteEquipmentSerializer(BaseSerializer):
    clear_resource = BooleanField(default=False)

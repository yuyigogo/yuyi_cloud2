from typing import Optional, Union

from bson import ObjectId

from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from mongoengine import DoesNotExist
from rest_framework.fields import BooleanField, CharField
from sites.models.site import Site

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH, SensorType
from common.error_code import StatusCode
from common.framework.exception import APIException, InvalidException
from common.framework.serializer import BaseSerializer


def get_equipment(equipment_id: str) -> Optional[ElectricalEquipment]:
    try:
        return ElectricalEquipment.objects.only("site_id").get(id=equipment_id)
    except DoesNotExist:
        raise InvalidException(f"invalid {equipment_id=}")


def get_customer_id(site_id: Union[ObjectId, str]) -> str:
    return str(Site.objects.only("customer").get(id=site_id).customer)


class CreatePointSerializer(BaseSerializer):
    measure_name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    measure_type = CharField(required=True)
    sensor_number = CharField(required=True)
    remarks = CharField(
        max_length=MAX_MESSAGE_LENGTH, allow_blank=True, allow_null=True
    )

    def validated_measure_name(self, measure_name):
        equipment_id = self.context["equipment_id"]
        if (
            MeasurePoint.objects(
                equipment_id=equipment_id, measure_name=measure_name
            ).count()
            > 0
        ):
            raise APIException(
                msg="测点名称已存在！", code=StatusCode.POINT_NAME_DUPLICATE.value
            )
        return measure_name

    def validate_measure_type(self, measure_type: str) -> str:
        if measure_type not in SensorType.values():
            raise APIException(f"invalid {measure_type=}")
        return measure_type

    def validate(self, data: dict) -> dict:
        equipment_id = self.context["equipment_id"]
        equipment = get_equipment(equipment_id)
        if (
            MeasurePoint.objects(
                measure_type=data["measure_type"], sensor_number=data["sensor_number"]
            ).count()
            > 0
        ):
            raise APIException("传感器编号已绑定！")
        data["site_id"] = str(equipment.site_id)
        data["customer_id"] = get_customer_id(equipment.site_id)
        return data


class UpdatePointSerializer(BaseSerializer):
    measure_name = CharField(max_length=MAX_LENGTH_NAME)
    measure_type = CharField()
    sensor_number = CharField()
    remarks = CharField(
        max_length=MAX_MESSAGE_LENGTH, allow_blank=True, allow_null=True
    )

    def validate_measure_name(self, measure_name):
        equipment_id = self.context["equipment_id"]
        point_id = self.context["point_id"]
        if (
            MeasurePoint.objects(
                equipment_id=equipment_id, measure_name=measure_name, id__ne=point_id
            ).count()
            > 0
        ):
            raise APIException(
                msg="测点名称已存在！", code=StatusCode.POINT_NAME_DUPLICATE.value
            )
        return measure_name

    def validate_measure_type(self, measure_type: str) -> str:
        if measure_type not in SensorType.values():
            raise APIException(f"invalid {measure_type=}")
        return measure_type

    def validate(self, data: dict) -> dict:
        equipment_id = self.context["equipment_id"]
        point_id = self.context["point_id"]
        try:
            point = MeasurePoint.objects.get(id=point_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {equipment_id=} or {point_id=}")
        self.context["point"] = point
        if point.measure_type != data["measure_type"]:
            # forbidden to modify the measure_type
            raise APIException("禁止修改已绑定传感器的测点类型!")
        self.context["changed_sensor_number"] = False
        if point.sensor_number != data["sensor_number"]:
            if MeasurePoint.objects(sensor_number=data["sensor_number"],).count() > 0:
                raise APIException("传感器编号已绑定！")
            self.context["changed_sensor_number"] = True
            equipment = get_equipment(equipment_id)
            self.context["site_id"] = str(equipment.site_id)
            self.context["customer_id"] = get_customer_id(equipment.site_id)
        return data


class DeletePointSerializer(BaseSerializer):
    clear_resource = BooleanField(default=False)

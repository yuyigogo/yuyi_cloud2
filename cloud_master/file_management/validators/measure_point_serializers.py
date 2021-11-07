from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from mongoengine import DoesNotExist
from rest_framework.fields import CharField

from common.const import MAX_LENGTH_NAME, MAX_MESSAGE_LENGTH
from common.framework.exception import InvalidException
from common.framework.serializer import BaseSerializer


class CreatePointSerializer(BaseSerializer):
    measure_name = CharField(required=True, max_length=MAX_LENGTH_NAME)
    measure_type = CharField(required=True)
    sensor_number = CharField(required=True)
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)

    def validate(self, data: dict) -> dict:
        equipment_id = self.context["equipment_id"]
        try:
            equipment = ElectricalEquipment.objects.get(id=equipment_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {equipment_id=}")
        return data


class UpdatePointSerializer(BaseSerializer):
    measure_name = CharField(max_length=MAX_LENGTH_NAME)
    measure_type = CharField()
    sensor_number = CharField()
    remarks = CharField(max_length=MAX_MESSAGE_LENGTH)

    def validate(self, data: dict) -> dict:
        equipment_id = self.context["equipment_id"]
        point_id = self.context["point_id"]
        try:
            point = MeasurePoint.objects.get(equipment_id=equipment_id, id=point_id)
        except DoesNotExist:
            raise InvalidException(f"invalid {equipment_id=} or {point_id=}")
        self.context["point"] = point
        return data

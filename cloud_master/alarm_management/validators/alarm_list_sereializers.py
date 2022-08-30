import logging
from typing import Optional

from alarm_management.models.alarm_info import AlarmInfo
from file_management.models.electrical_equipment import ElectricalEquipment
from rest_framework.fields import BooleanField, CharField, IntegerField
from sites.models.site import Site

from common.const import MAX_MESSAGE_LENGTH, AlarmLevel, AlarmType, SensorType
from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer, PageLimitSerializer


def validate_site_or_equipment(
    cls, site_id: Optional[str] = None, equipment_id: Optional[str] = None
) -> int:
    assert site_id or equipment_id, "should have one value in site_id or equipment_id "
    if site_id:
        return Site.objects(id=site_id).count()
    else:
        return ElectricalEquipment.objects(id=equipment_id).count()


class AlarmListSerializer(PageLimitSerializer):
    alarm_type = IntegerField(required=True)
    start_date = CharField(required=False)
    end_date = CharField(required=False)
    sensor_type = CharField(required=False)
    alarm_level = IntegerField(required=False)
    is_processed = BooleanField(default=None, allow_null=True)

    def validate_alarm_level(self, alarm_level: int) -> int:
        if alarm_level not in AlarmLevel.values():
            raise APIException(f"invalid {alarm_level=}!")
        return alarm_level

    def validate_sensor_type(self, sensor_type):
        if sensor_type not in SensorType.values():
            raise APIException(f"invalid {sensor_type=}")
        return sensor_type

    def validate_alarm_type(self, alarm_type):
        if alarm_type not in AlarmType.values():
            raise APIException(f"invalid {alarm_type=}")
        return alarm_type

    def validate(self, data):
        site_id = self.context.get("site_id")
        equipment_id = self.context.get("equipment_id")
        if not validate_site_or_equipment(site_id, equipment_id):
            raise APIException(f"invalid {site_id=} or {equipment_id=}")
        return data


class AlarmActionSerializer(BaseSerializer):
    is_processed = BooleanField(required=True, default=True)
    processed_remarks = CharField(required=False, max_length=MAX_MESSAGE_LENGTH)

    def validate(self, data: dict) -> dict:
        alarm_id = self.context["alarm_id"]
        try:
            alarm_info = AlarmInfo.objects.get(id=alarm_id)
        except Exception as e:
            logging.exception(f"invalid {alarm_id=} with {e=}")
            raise APIException(f"invalid {alarm_id=}")
        data["alarm_info"] = alarm_info
        return data

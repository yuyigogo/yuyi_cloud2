from rest_framework.fields import BooleanField, CharField, IntegerField

from common.const import AlarmLevel, SensorType
from common.framework.exception import APIException
from common.framework.serializer import PageLimitSerializer


class SensorListSerializer(PageLimitSerializer):
    point_id = CharField(required=False)
    alarm_level = IntegerField(required=False)
    is_online = BooleanField(required=False)
    sensor_type = CharField(required=False)

    def validate_alarm_level(self, alarm_level: int) -> int:
        if alarm_level not in AlarmLevel.values():
            raise APIException(f"invalid {alarm_level=}!")
        return alarm_level

    def validate_sensor_type(self, sensor_type):
        if sensor_type not in SensorType.values():
            raise APIException(f"invalid {sensor_type=}")
        return sensor_type

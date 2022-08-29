import logging

from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from rest_framework.fields import BooleanField, CharField, IntegerField

from common.const import AlarmLevel, SensorType
from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer, PageLimitSerializer

logger = logging.getLogger(__name__)


class SensorListSerializer(PageLimitSerializer):
    point_id = CharField(required=False)
    alarm_level = IntegerField(required=False)
    is_online = BooleanField(default=None, allow_null=True)
    sensor_type = CharField(required=False)

    def validate_alarm_level(self, alarm_level: int) -> int:
        if alarm_level not in AlarmLevel.values():
            raise APIException(f"invalid {alarm_level=}!")
        return alarm_level

    def validate_sensor_type(self, sensor_type):
        if sensor_type not in SensorType.values():
            raise APIException(f"invalid {sensor_type=}")
        return sensor_type


class SensorDetailsSerializer(BaseSerializer):
    def validate(self, data):
        sensor_obj_id = self.context["pk"]
        sensor_type = self.context["sensor_type"].upper()
        if sensor_type not in SensorType.values():
            raise APIException(f"Invalid {sensor_type=}")
        try:
            my_col = MONGO_CLIENT[sensor_type]
            sensor_data = my_col.find_one({"_id": sensor_obj_id})
        except Exception as e:
            logger.exception(f"get sensor_obj failed with {e=}")
            raise APIException(f"Invalid {sensor_obj_id=}-{sensor_type=}")
        self.context["sensor_obj_dict"] = bson_to_dict(sensor_data)
        return data

import logging

from equipment_management.models.sensor_config import SensorConfig
from mongoengine import DoesNotExist, MultipleObjectsReturned
from rest_framework.fields import CharField, IntegerField

from common.const import SensorType
from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer

logger = logging.getLogger(__name__)


class PubSensorConfigSerializer(BaseSerializer):
    upload_interval = IntegerField(required=True)

    def validate(self, data):
        client_number = self.context["client_number"]
        sensor_id = self.context["sensor_id"]
        try:
            sensor_config = SensorConfig.objects.only("sensor_type").get(
                sensor_number=sensor_id, client_number=client_number
            )
        except DoesNotExist:
            raise APIException(f"invalid {client_number=} or {sensor_id=}")
        data["sensor_type"] = sensor_config.sensor_type
        return data


class PubMultiSensorConfigSerializer(BaseSerializer):
    sensor_id = CharField(required=True)
    sensor_type = CharField(required=True)
    upload_interval = IntegerField(required=True)

    def validate_sensor_type(self, sensor_type):
        if sensor_type not in SensorType.values():
            raise APIException(f"invalid {sensor_type=}")
        return sensor_type

    def validate(self, data: dict) -> dict:
        sensor_id = data["sensor_id"]
        try:
            sensor_config = SensorConfig.objects.only("site_id").get(
                sensor_number=sensor_id
            )
        except (DoesNotExist, MultipleObjectsReturned) as e:
            logger.exception(f"get sensor_config {e=}")
            raise APIException(f"invalid {sensor_id=}")
        data["site_id"] = sensor_config.site_id
        return data

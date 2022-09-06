from equipment_management.models.sensor_config import SensorConfig
from mongoengine import DoesNotExist

from common.framework.exception import APIException
from common.framework.serializer import BaseSerializer


class PubSensorConfigSerializer(BaseSerializer):
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

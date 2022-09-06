import logging

from cloud.settings import MONGO_CLIENT
from cloud_mqtt.cloud_mqtt_client import cloud_mqtt_client
from cloud_mqtt.deal_with_publish_message import BASE_SENSOR_SAMPLE_PERIOD_PUBLISH_TOPIC
from equipment_management.models.sensor_config import SensorConfig
from equipment_management.validators.pub_sensor_config_serializers import (
    PubMultiSensorConfigSerializer,
    PubSensorConfigSerializer,
)
from rest_framework.status import HTTP_400_BAD_REQUEST

from common.framework.response import BaseResponse
from common.framework.view import BaseView

logger = logging.getLogger(__name__)


class SensorConfigView(BaseView):
    """get/update the upload_interval value for sensor"""

    def get(self, request, client_number, sensor_id):
        data, _ = self.get_validated_data(
            PubSensorConfigSerializer, gateway_id=client_number, sensor_id=sensor_id
        )
        sensor_type = data["sensor_type"]
        my_col = MONGO_CLIENT[sensor_type]
        raw_query = {"sensor_id": sensor_id, "is_latest": True}
        projection = {"upload_interval": 1}
        data = my_col.find_one(raw_query, projection)
        upload_interval = data.get("upload_interval")
        return BaseResponse(data={"upload_interval": upload_interval})

    def put(self, request, client_number, sensor_id):
        data, _ = self.get_validated_data(
            PubSensorConfigSerializer, gateway_id=client_number, sensor_id=sensor_id
        )
        logger.info(
            f"{request.user.username} request update sensor upload_interval with {client_number=}, {sensor_id=} by mqtt publish client"
        )
        payload = {"params": {"period": data["upload_interval"]}}
        try:
            cloud_mqtt_client.mqtt_publish(
                f"/{client_number}subnode/{sensor_id}/{BASE_SENSOR_SAMPLE_PERIOD_PUBLISH_TOPIC}",
                payload,
            )
        except Exception as e:
            logger.exception(
                f"update sensor's upload_interval failed in mqtt with {e=}"
            )
            return BaseResponse(status_code=HTTP_400_BAD_REQUEST)
        return BaseResponse()


class SensorConfigsView(BaseView):
    """同种批量应用"""

    def put(self, request):
        data, _ = self.get_validated_data(PubMultiSensorConfigSerializer)
        logger.info(
            f"{request.user.username} request update multi sensor's upload_interval with {data=}"
        )
        site_id = data["site_id"]
        sensor_type = data["sensor_type"]
        sensor_id_client_number = SensorConfig.objects.filter(
            site_id=site_id, sensor_type=sensor_type
        ).values_list("sensor_number", "client_number")
        payload = {"params": {"period": data["upload_interval"]}}
        for (sensor_id, client_number) in sensor_id_client_number:
            try:
                cloud_mqtt_client.mqtt_publish(
                    f"/{client_number}subnode/{sensor_id}/{BASE_SENSOR_SAMPLE_PERIOD_PUBLISH_TOPIC}",
                    payload,
                )
            except Exception as e:
                logger.exception(
                    f"update sensor's upload_interval failed in mqtt with {e=}"
                )
                pass
        return BaseResponse()

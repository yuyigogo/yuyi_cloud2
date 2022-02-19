import logging
import re

from cloud.settings import CLIENT_IDS
from equipment_management.models.gateway import GateWay
from equipment_management.services.sensor_config_service import SensorConfigService
from mongoengine import DoesNotExist

from common.const import MODEL_KEY_TO_SENSOR_TYPE
from common.storage.redis import redis

# this file is to add the corresponding subscribe and published topics
# and each topic is paired

# 获取网关下传感器列表的主题
BASE_GATEWAY_SUBSCRIBE_TOPIC = "/serivice_reply/sub_get"
BASE_GATEWAY_PUBLISH_TOPIC = "/serivice/sub_get"
# 匹配网关下传感器列表
SENSORS_IN_GATEWAY_PATTERN = re.compile(
    rf"/(?P<client_id>[a-zA-Z0-9]+){BASE_GATEWAY_SUBSCRIBE_TOPIC}"
)

logger = logging.getLogger(__name__)


class OnMqttMessage(object):
    @classmethod
    def is_gateway_enabled(cls, client_id: str) -> bool:
        return redis.sismember(CLIENT_IDS, client_id)

    @classmethod
    def deal_with_msg(cls, topic: str, msg_dict: dict):
        """处理mqtt server PUBLISH 回调总入口"""
        if ret := SENSORS_IN_GATEWAY_PATTERN.match(topic):
            client_id = ret.group(1)
            cls.deal_with_sensors_in_gateway_msg(client_id, msg_dict)

    @classmethod
    def deal_with_sensors_in_gateway_msg(cls, client_id: str, msg_dict: dict):
        """网关下传感器列表数据存储"""
        logger.info(f"deal_with_sensors_in_gateway_msg for {client_id=}")
        if not cls.is_gateway_enabled(client_id):
            return
        try:
            gateway = GateWay.objects.get(client_number=client_id)
        except DoesNotExist:
            logger.error(f"{client_id=} in redis, but not find in mongodb")
            return
        logger.info(f"*****************")
        params = msg_dict.get("params", {})
        sensors_ids = params.get("sensor", [])
        model_keys = params.get("modelkey", [])
        sensor_types = [MODEL_KEY_TO_SENSOR_TYPE[model_key] for model_key in model_keys]
        current_sensors = set(zip(sensors_ids, sensor_types))
        existing_sensors = set(list(gateway.sensor_ids))
        new_sensors = current_sensors - existing_sensors
        all_sensors = list(current_sensors | existing_sensors)
        gateway.update(sensor_ids=all_sensors)
        if new_sensors is not None:
            # create sensor_config model
            SensorConfigService(client_id).bulk_insert_sensor_configs(new_sensors)

import logging
import re

from cloud.settings import CLIENT_IDS

# 获取网关下传感器列表的主题
from equipment_management.models.sensor_config import SensorConfig
from pymongo import UpdateOne

from common.storage.redis import redis

# this file is to add the corresponding subscribe and published topics
# and each topic is paired

# 网关下传感器列表主题
BASE_GATEWAY_SUBSCRIBE_TOPIC = "/serivice_reply/sub_get"
BASE_GATEWAY_PUBLISH_TOPIC = "/serivice/sub_get"
# 匹配网关下传感器列表
SENSORS_IN_GATEWAY_PATTERN = re.compile(
    rf"/(?P<client_id>[a-zA-Z0-9]+){BASE_GATEWAY_SUBSCRIBE_TOPIC}"
)

# 采集周期设置主题
BASE_SENSOR_SAMPLE_PERIOD_PUBLISH_TOPIC = "/common/service/sample_period_set"
BASE_SENSOR_SAMPLE_PERIOD_SUBSCRIBE_TOPIC = "/common/service_reply/sample_period_set"
SENSOR_PERIOD_PATTERN = re.compile(
    rf"/(?P<gateway_id>[a-zA-Z0-9]+)/subnode/(?P<sensor_id>[a-zA-Z0-9]+){BASE_SENSOR_SAMPLE_PERIOD_SUBSCRIBE_TOPIC}"
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
            logger.info(f"{client_id=} is not active!")
            return
        params = msg_dict.get("params", [])
        bulk_operations = [
            UpdateOne(
                {"sensor_number": param["sensor_id"]},
                {
                    "$set": {
                        "model_key": param["modelkey"],
                        "can_senor_online": param["sensor_online"],
                        "communication_mode": param["sensor_comm_mode"],
                    }
                },
            )
            for param in params
        ]
        collection = SensorConfig._get_collection()
        collection.bulk_write(bulk_operations, ordered=False)


# msg_dict = {"params":[
#     {
#         "sensor_id": "584e500400200002",
#         "modelkey": "0000000000000002",
#         "sensor_online": 0,
#         "sensor_comm_mode": "RS485"
#     },
#     {
#         "sensor_id": "584e500400200005",
#         "modelkey": "0000000000000005",
#         "sensor_online": 1,
#         "sensor_comm_mode": "LoRa"
#     },
#     {
#         "sensor_id": "584e50040020000b",
#         "modelkey": "0000000000000004",
#         "sensor_online": 0,
#         "sensor_comm_mode": "LoRaWan"
#     },
#     {
#         "sensor_id": "584e50040020000e",
#         "modelkey": "0000000000000006",
#         "sensor_online": 1,
#         "sensor_comm_mode": "433MHz"
#     },
# ]}
# OnMqttMessage.deal_with_sensors_in_gateway_msg("", msg_dict)

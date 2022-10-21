"""
This script is to subscribe message from mqtt, and push msg to redis(list).
"""

import datetime
import json
import os
import re

from cloud.settings import MQTT_CLIENT_CONFIG, CLIENT_IDS
from paho.mqtt import client as mqtt_client

from common.const import CLOUD_SUBSCRIBE_MSG_LIST, MsgQueueType, SENSOR_INFO_PREFIX
from common.storage.redis import msg_queue_redis, normal_redis


class SyncSubscribeMsg:
    """
    just push matched data into redis
    """

    SENSOR_DATA_PATTERN = re.compile(
        r"/(?P<gateway_id>[a-zA-Z0-9]+)/subnode/(?P<sensor_id>[a-zA-Z0-9]+)/data_ctrl/property"
    )
    SENSOR_ALARM_PATTERN = re.compile(
        r"/(?P<gateway_id>[a-zA-Z0-9]+)/subnode/(?P<sensor_id>[a-zA-Z0-9]+)/common/event"
    )

    def __init__(self, client_id, host, port):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.client = mqtt_client.Client(self.client_id)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print(
            f"{datetime.datetime.now()} DataLoader connected with result code "
            + str(rc)
        )
        client.subscribe("#")  # 订阅消息

    @staticmethod
    def on_message(client, userdata, msg):
        topic = msg.topic
        sensor_data_ret = SyncSubscribeMsg.SENSOR_DATA_PATTERN.match(
            msg.topic
        )  # 采集数据上传
        alarm_ret = SyncSubscribeMsg.SENSOR_ALARM_PATTERN.match(topic)  # 传感器报警
        re_ret = sensor_data_ret or alarm_ret
        if re_ret is not None:
            gateway_id, sensor_id = re_ret.groups()[0], re_ret.groups()[1]
            if not SyncSubscribeMsg.can_precessing(gateway_id, sensor_id):
                return
            if sensor_data_ret is not None:
                msg_queue_type = MsgQueueType.DATA_LOADER.value
            elif alarm_ret is not None:
                msg_queue_type = MsgQueueType.SENSOR_ALARM.value
            else:
                print("undefined msg_queue_type!")
                return
            print("************* matched data has been configured, push it to redis! ***********************")
            queue_data = {
                "msg_queue_type": msg_queue_type,
                "gateway_id": gateway_id,
                "sensor_id": sensor_id,
                "msg_str": msg.payload.decode("utf-8"),
            }
            msg_queue_redis.lpush(CLOUD_SUBSCRIBE_MSG_LIST, json.dumps(queue_data))

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)

    @staticmethod
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("DataLoader Unexpected disconnection %s" % rc)
        else:
            print("DataLoader disconnection !!!")

    @classmethod
    def can_precessing(cls, gateway_id: str, sensor_id: str) -> bool:
        sensor_info_key = f"{SENSOR_INFO_PREFIX}{sensor_id}"
        # 网关已启用且档案已配置才会入库
        return normal_redis.sismember(CLIENT_IDS, gateway_id) and normal_redis.exists(
            sensor_info_key
        )

    def run(self):
        self.client.username_pw_set(
            MQTT_CLIENT_CONFIG["user"], MQTT_CLIENT_CONFIG["pw"]
        )
        self.client.on_connect = SyncSubscribeMsg.on_connect
        self.client.on_message = SyncSubscribeMsg.on_message
        self.client.on_subscribe = SyncSubscribeMsg.on_subscribe
        self.client.on_disconnect = SyncSubscribeMsg.on_disconnect
        self.client.connect(self.host, self.port, 60)
        self.client.loop_forever()


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloud.settings")
    subscribe_client_id = MQTT_CLIENT_CONFIG.get("subscribe_client_id", "")
    host = MQTT_CLIENT_CONFIG.get("host", "")
    port = MQTT_CLIENT_CONFIG.get("port", "")
    sync_subscribe_msg = SyncSubscribeMsg(subscribe_client_id, host, port)
    try:
        sync_subscribe_msg.run()
    except Exception as e:
        print(e)

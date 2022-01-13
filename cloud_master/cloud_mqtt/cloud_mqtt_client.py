import json
import logging

import paho.mqtt.client as mqtt_client
from bson import ObjectId

from cloud.settings import MQTT_CLIENT_CONFIG

logger = logging.getLogger(__name__)


class CloudMqtt(object):
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.client = mqtt_client.Client(self.client_id, clean_session=False)

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"{self.client_id} success to connected to MQTT Broker!")
        else:
            logger.info(f"{self.client_id} failed to connect to MQTT Broker!")
        # todo specify topics
        # client.subscribe("/8e01000213000283/serivice_reply/sub_get")
        # client.subscribe("/8E00000213000265/serivice_reply/sub_get")
        # sensors_subscribe_topics()  # 订阅消息
        # cmd_send_login()  #

    @staticmethod
    def on_mqtt_message(client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        logger.info(f"{msg.topic=}, {str(msg.payload)}")
        print(msg.topic)
        print(2222)
        print(msg.payload)
        # todo add corresponding function to deal with subscribed topics

    @staticmethod
    def on_mqtt_subscribe(client, userdata, mid, granted_qos):
        logger.info(f"On Subscribed: {mid=}, {userdata=}, {granted_qos=}")

    @staticmethod
    def on_mqtt_disconnect(client, userdata, rc):
        if rc != 0:
            logger.info(f"Unexpected disconnection {rc=}")
        else:
            logger.info("disconnection !!!")

    def mqtt_publish(self, topic, payload=None):
        if not payload:
            payload = {}
        payload.update({"id": "123", "version": "1.0"})
        self.client.publish(topic, payload=json.dumps(payload), qos=0)

    def run(self):
        self.client.username_pw_set(MQTT_CLIENT_CONFIG["user"], MQTT_CLIENT_CONFIG["pw"])
        self.client.on_connect = self.on_mqtt_connect
        self.client.on_message = self.on_mqtt_message
        self.client.on_subscribe = self.on_mqtt_subscribe
        self.client.on_disconnect = self.on_mqtt_disconnect
        self.client.connect_async(MQTT_CLIENT_CONFIG["host"], MQTT_CLIENT_CONFIG["port"], 60)
        self.client.loop_start()
        return self


cloud_mqtt_client = CloudMqtt(str(ObjectId())).run()





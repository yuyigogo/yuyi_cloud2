import datetime
import json
import re
from copy import deepcopy

import dateutil.parser
import redis
from cloud.settings import (
    MQTT_CLIENT_CONFIG,
    REDIS_HOST,
    REDIS_PORT,
    MONGO_CLIENT,
)
from paho.mqtt import client as mqtt_client

from common.const import SensorType

uhf_loading_data, ae_tev_loading_data = {}, {}

sensor_redis_cli = redis.Redis(
    connection_pool=redis.ConnectionPool(
        host=REDIS_HOST, port=REDIS_PORT, db=5, decode_responses=True
    )
)


class DataLoader:
    """
    just load data into mongodb
    """

    collection_mapping = {"二合一传感器": "ae_tev", "特高频传感器": "uhf", "温度传感器": "temperature"}

    pattern = re.compile(
        r"/(?P<client_id>[a-zA-Z0-9]+)/subnode/(?P<sensor_id>[a-zA-Z0-9]+)/data_ctrl/property"
    )

    def __init__(self, client_id, host, port):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.client = mqtt_client.Client(self.client_id)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print(f"{datetime.datetime.now()} Connected with result code " + str(rc))
        client.subscribe("#")  # 订阅消息
        # client.subscribe("8E001302000001A5")  # 订阅消息

    @staticmethod
    def get_sensor_type(msg_dict):
        params = msg_dict.get("params", {})
        if "TEV" in params or "AE" in params:
            return SensorType.ae_tev()
        elif "Temp" in params:
            return SensorType.temp.value
        elif "UHF" in params:
            return SensorType.uhf.value
        else:
            return ""

    @staticmethod
    def insert(client_id, sensor_id, sensor_type, msg_dict):
        cur_time = dateutil.parser.parse(datetime.datetime.now().isoformat())
        my_col = MONGO_CLIENT[sensor_type]
        my_query = {"is_new": True, "sensor_id": sensor_id}
        new_values = {"$set": {"is_new": False, "update_time": cur_time}}
        my_col.update_many(my_query, new_values)
        params = msg_dict.get("params", {})
        if sensor_type == SensorType.ae.value:
            params.pop("TEV")
        if sensor_type == SensorType.tev.value:
            params.pop("AE")
        data = {
            "client_id": client_id,
            "sensor_id": sensor_id,
            "version": msg_dict.get("version", ""),
            "sensor_type": sensor_type,
            "params": params,
            "create_time": cur_time,
            "update_time": cur_time,
            "is_new": True,
        }
        insert_res = my_col.insert_one(data)
        if insert_res.acknowledged:
            print(f"inset data succeed for {sensor_type}, {sensor_id=}, {client_id=}!")
        else:
            print(f"inset data failed with {msg_dict=}!")

    @staticmethod
    def on_message(client, userdata, msg):
        print(f"time: {datetime.datetime.now()} msg.topic:{msg.topic}")
        ret = DataLoader.pattern.match(msg.topic)
        if ret is not None:
            client_id, sensor_id = ret.groups()[0], ret.groups()[1]
            print(f"matched for {client_id=}, {sensor_id=}")
            try:
                if sensor_redis_cli.sismember("client_ids", client_id):

                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    sensor_type = DataLoader.get_sensor_type(msg_dict)
                    if sensor_type:
                        if sensor_type == SensorType.ae_tev():
                            for sensor_type in SensorType.ae_tev():
                                DataLoader.insert(
                                    client_id,
                                    sensor_id,
                                    sensor_type,
                                    deepcopy(msg_dict),
                                )
                        else:
                            DataLoader.insert(
                                client_id, sensor_id, sensor_type, msg_dict
                            )
            except Exception as e:
                print(e)

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)

    @staticmethod
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection %s" % rc)
        else:
            print("disconnection !!!")

    def run(self):
        self.client.username_pw_set("guest", "guest")
        self.client.on_connect = DataLoader.on_connect
        self.client.on_message = DataLoader.on_message
        self.client.on_subscribe = DataLoader.on_subscribe
        self.client.on_disconnect = DataLoader.on_disconnect
        self.client.connect(self.host, self.port, 60)
        self.client.loop_forever()


subscribe_client_id = MQTT_CLIENT_CONFIG.get("subscribe_client_id", "")
host = MQTT_CLIENT_CONFIG.get("host", "")
port = MQTT_CLIENT_CONFIG.get("port", "")
data_loader = DataLoader(subscribe_client_id, host, port)

if __name__ == "__main__":
    data_loader.run()

import datetime
import json
import re
from typing import Optional

from bson import ObjectId
from cloud.settings import MONGO_CLIENT, MQTT_CLIENT_CONFIG
from cloud_ws.ws_group_send import WsSensorDataSend
from equipment_management.models.sensor_config import SensorConfig
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from paho.mqtt import client as mqtt_client

from common.const import (
    SENSOR_INFO_PREFIX,
    AlarmFlag,
    AlarmLevel,
    AlarmType,
    SensorType,
)
from common.storage.redis import redis
from common.utils import datetime_from_str


class DataLoader:
    """
    just load data into mongodb
    """

    pattern = re.compile(
        r"/(?P<gateway_id>[a-zA-Z0-9]+)/subnode/(?P<sensor_id>[a-zA-Z0-9]+)/data_ctrl/property"
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

    @classmethod
    def get_or_set_sensor_info_from_redis(cls, sensor_id: str) -> Optional[dict]:
        sensor_info_key = f"{SENSOR_INFO_PREFIX}{sensor_id}"
        data_from_redis = redis.hgetall(sensor_info_key)
        if data_from_redis:
            return {
                key.decode(): value.decode() for key, value in data_from_redis.items()
            }
        else:
            # todo get from sensor_config model, use lru_cache
            try:
                point = MeasurePoint.objects.only("equipment_id").get(
                    sensor_number=sensor_id
                )
                equipment_id = str(point.equipment_id)
                point_id = str(point.id)
                equipment = ElectricalEquipment.objects.only("site_id").get(
                    id=equipment_id
                )
                site_id = str(equipment.site_id)
                # todo change this value when name changed or delete
                sensor_info = {
                    "point_id": point_id,
                    # "measure_name": point.measure_name,
                    "equipment_id": equipment_id,
                    # "device_name": equipment.device_name,
                    "site_id": site_id,
                }
            except Exception as e:
                print(f"get sensor: {sensor_id=} info error with exception: {e=}")
                return
            # set sensor_info to redis
            redis.hmset(sensor_info_key, sensor_info)

    @classmethod
    def insert_and_update_alarm_info(cls, sensor_obj_dict: dict) -> Optional[dict]:
        sensor_id = sensor_obj_dict["sensor_id"]
        alarm_info = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_obj_dict["sensor_type"],
            "client_number": sensor_obj_dict["client_number"],
            "is_latest": True,
            "alarm_type": AlarmType.POINT_ALARM.value,
            "alarm_level": sensor_obj_dict["alarm_level"],
            "alarm_describe": sensor_obj_dict["alarm_describe"],
            "sensor_data_id": sensor_obj_dict["_id"],
            "is_online": True,
            "is_processed": False,
        }
        sensor_info = cls.get_or_set_sensor_info_from_redis(sensor_id)
        if not sensor_info:
            print(f"can't get sensor_info in insert alarm data:{sensor_id=}")
            return
        alarm_info.update(sensor_info)
        my_col = MONGO_CLIENT["alarm_info"]
        # insert new sensor data
        my_col.insert_one(alarm_info)
        # update is_latest filed to false
        my_query = {"is_latest": True, "sensor_id": sensor_id}
        new_values = {"$set": {"is_latest": False}}
        my_col.update_many(my_query, new_values)
        return alarm_info

    @classmethod
    def insert_and_update_sensor_data(
        cls, sensor_type: str, gateway_id: str, sensor_id: str, sensor_data: dict
    ) -> Optional[dict]:
        """
        1. insert new sensor data to db;
        2. update old sensor data's is_latest to false
        """
        try:
            parsed_sensor_dict = cls.parse_origin_sensor_data(
                sensor_type, gateway_id, sensor_id, sensor_data
            )
            my_col = MONGO_CLIENT[sensor_type]
            # insert new sensor data
            my_col.insert_one(parsed_sensor_dict)
        except Exception as e:
            print(f"***************insert new sensor data error with {e=}")
            return
        my_query = {"is_latest": True, "sensor_id": sensor_id}
        new_values = {"$set": {"is_latest": False}}
        my_col.update_many(my_query, new_values)
        return parsed_sensor_dict

    @classmethod
    def parse_origin_sensor_data(
        cls, sensor_type: str, gateway_id: str, sensor_id: str, sensor_data: dict
    ) -> dict:
        parsed_dict = {
            "_id": ObjectId(),
            "sensor_type": sensor_type,
            "client_number": gateway_id,
            "sensor_id": sensor_id,
            "is_latest": True,
            "is_online": True,
        }
        params = sensor_data.get("params", {})
        # if sensor_type in [SensorType.ae.value, SensorType.tev.value, SensorType.temp.value, SensorType.uhf.vale]:
        if sensor_type != SensorType.mech:
            parsed_dict.update(params.get("status", {}))
            parsed_dict.update(params.get("wparam", {}))
            data = params.get("data", {})
            parsed_dict["create_time"] = datetime_from_str(data["acqtime"])
            parsed_dict["alarm_flag"] = data.get("alert_flag", AlarmFlag.NO_PUSH.value)
            parsed_dict["alarm_level"] = data.gvet(
                "alert_level", AlarmLevel.NORMAL.value
            )
            parsed_dict["alarm_describe"] = data.get("alert_describe", "")
            if sensor_type == SensorType.ae:
                parsed_dict["maxvalue"] = data.get("maxvalue")
                parsed_dict["rmsvalue"] = data.get("rmsvalue")
                parsed_dict["harmonic1"] = data.get("harmonic1")
                parsed_dict["harmonic2"] = data.get("harmonic2")
                parsed_dict["gain"] = data.get("gain")
            elif sensor_type == SensorType.tev:
                parsed_dict["amp"] = data.get("amp")
            elif sensor_type == SensorType.temp:
                parsed_dict["T"] = data.get("T")
            else:
                # uhf
                parsed_dict["prps"] = data.get("prps", [])
                parsed_dict["rangemax"] = data.get("rangemax")
                parsed_dict["rangemin"] = data.get("rangemin")
                parsed_dict["filter"] = data.get("filter")
                parsed_dict["np"] = data.get("np")
                parsed_dict["gpp"] = data.get("gpp")
                parsed_dict["ampmax"] = data.get("ampmax")
                parsed_dict["ampmean"] = data.get("ampmean")
        else:
            # Mech
            parsed_dict["create_time"] = datetime_from_str(sensor_data["acqtime"])
            parsed_dict["Mech_On_Coil_I"] = params.get("Mech_On_Coil_I", {})
            parsed_dict["Mech_Off_Coil_I"] = params.get("Mech_Off_Coil_I", {})
            parsed_dict["Mech_Motor_I"] = params.get("Mech_Motor_I", {})
            parsed_dict["Mech_CT_A_V"] = params.get("Mech_CT_A_V", {})
            parsed_dict["Mech_CT_B_V"] = params.get("Mech_CT_B_V", {})
            parsed_dict["Mech_CT_C_V"] = params.get("Mech_CT_C_V", {})
            parsed_dict["Mech_DIS_I"] = params.get("Mech_DIS_I", {})
            mech_results = params.get("Mech_Results", {})
            parsed_dict["alarm_flag"] = mech_results.get(
                "alert_flag", AlarmFlag.NO_PUSH.value
            )
            parsed_dict["alarm_level"] = mech_results.get(
                "alert_level", AlarmLevel.NORMAL.value
            )
            parsed_dict["alarm_describe"] = mech_results.get("alert_describe", "")
        return parsed_dict

    @classmethod
    def deal_with_sensor_data(cls, gateway_id: str, sensor_id: str, sensor_data: dict):
        """
        1. store sensor data to db;
        2. store alarm data to db;
        3. push data from ws;
        """
        sensor_type = sensor_data.get("sensor_type")
        if sensor_type not in SensorType.values():
            print(f"************invalid {sensor_type=}")
            return
        new_obj_dict = cls.insert_and_update_sensor_data(
            sensor_type, gateway_id, sensor_id, sensor_data
        )
        if not new_obj_dict:
            return
        alarm_info = cls.insert_and_update_alarm_info(new_obj_dict)
        # ws: 1. push alarm data; 2. sensor_list data
        cls.deal_with_ws_data(new_obj_dict, alarm_info)

    @classmethod
    def deal_with_ws_data(cls, sensor_data: dict, alarm_data: dict):
        sensor_id = sensor_data["sensor_id"]
        WsSensorDataSend(sensor_id).ws_send(sensor_data)
        pass

    @staticmethod
    def on_message(client, userdata, msg):
        print(f"time: {datetime.datetime.now()} msg.topic:{msg.topic}")
        ret = DataLoader.pattern.match(msg.topic)
        if ret is not None:
            gateway_id, sensor_id = ret.groups()[0], ret.groups()[1]
            # 网关已启用且档案已配置才会入库
            try:
                if (
                    redis.sismember("client_ids", gateway_id)
                    and SensorConfig.objects(sensor_number=sensor_id).count() > 0
                ):
                    print(f"matched for {gateway_id=}, {sensor_id=}")
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    DataLoader.deal_with_sensor_data(gateway_id, sensor_id, msg_dict)
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
        self.client.username_pw_set(
            MQTT_CLIENT_CONFIG["user"], MQTT_CLIENT_CONFIG["pw"]
        )
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
    try:
        data_loader.run()
    except Exception as e:
        print(e)

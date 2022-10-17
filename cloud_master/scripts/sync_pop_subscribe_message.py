"""
This script is to pop msg from redis queue, and do following things:
    1. store sensor data;
    2. store alarm data;
    3. push alarm data with ws.
"""
import json
import logging
import time
import traceback
from typing import Optional

from alarm_management.models.alarm_info import AlarmInfo
from bson import ObjectId
from cloud.settings import MONGO_CLIENT
from cloud_home.services.abnormal_count_service import AbnormalCacheService

from common.const import (
    CLOUD_SUBSCRIBE_MSG_LIST,
    SENSOR_INFO_PREFIX,
    SITE_UNPROCESSED_NUM,
    AlarmFlag,
    AlarmLevel,
    AlarmType,
    MsgQueueType,
    SensorType,
)
from common.framework.service import SensorConfigService
from common.storage.redis import msg_queue_redis, normal_redis
from common.utils import datetime_from_str

logger = logging.getLogger(__name__)


class SyncPopMsg(object):
    @classmethod
    def run(cls):
        while True:
            logger.info("-------------start to run sync_pop_msg task------------")
            while msg_queue_redis.llen(CLOUD_SUBSCRIBE_MSG_LIST):
                try:
                    handle_data = msg_queue_redis.rpop(CLOUD_SUBSCRIBE_MSG_LIST)
                    data = json.loads(handle_data)
                    cls.deal_with_msg_queue(data)
                except Exception as e:
                    logger.exception("deal_with_msg_queue error with exception: {e}")
                    logger.warning(f"{traceback.format_exc()}")
            time.sleep(5)

    @classmethod
    def deal_with_msg_queue(cls, data: dict):
        msg_queue_type = data["msg_queue_type"]
        gateway_id = data["gateway_id"]
        sensor_id = data["sensor_id"]
        msg_dict = json.loads(data["msg_str"])
        if msg_queue_type == MsgQueueType.DATA_LOADER:
            cls.deal_with_sensor_data(gateway_id, sensor_id, msg_dict)
        else:
            cls.deal_with_sensor_alarm()

    @classmethod
    def deal_with_sensor_data(cls, gateway_id: str, sensor_id: str, sensor_data: dict):
        """
        1. store sensor data to db;
        2. store alarm data to db;
        3. push data from ws;
        """
        if not cls.can_precessing(gateway_id, sensor_id):
            logger.warning(
                f"this msg can't be processed with {gateway_id=}, {sensor_id=}"
            )
            return
        logger.info(f"begin to process sensor_data_ret for {gateway_id=}, {sensor_id=}")
        sensor_type = sensor_data.get("sensor_type")
        if sensor_type not in SensorType.values():
            logger.warning(f"************invalid {sensor_type=}")
            return
        new_obj_dict = cls.insert_and_update_sensor_data(
            sensor_type, gateway_id, sensor_id, sensor_data
        )
        if not new_obj_dict:
            return
        alarm_info = cls.insert_and_update_alarm_info(new_obj_dict)
        if alarm_info["alarm_level"] in AlarmLevel.abnormal_alarm_level():
            # increment customer/site day/week/month's alarm num
            service = AbnormalCacheService(
                customer_id=alarm_info["customer_id"], site_id=alarm_info["site_id"]
            )
            service.auto_increment_customer_abnormal_infos()
            service.auto_increment_site_abnormal_infos()
        # ws: 1. push alarm data; 2. sensor_list data
        cls.deal_with_ws_data(new_obj_dict, alarm_info)

    @classmethod
    def deal_with_sensor_alarm(cls, gateway_id: str, sensor_id: str, origin_data: dict):
        """
        This method is to deal with sensor alarm(alarm type is SENSOR_ALARM).
        when a point alarm has happened, the following thing need to do:
            1. insert a new data in alarm_info;
            2. update the corresponding record's is_online field;
        """
        if not cls.can_precessing(gateway_id, sensor_id):
            logger.warning(
                f"this msg can't be processed with {gateway_id=}, {sensor_id=}"
            )
            return
        sensor_type = origin_data.get("sensor_type")
        if sensor_type not in SensorType.values():
            logger.warning(f"************invalid {sensor_type=}")
            return
        parsed_dict = {
            "_id": ObjectId(),
            "sensor_type": sensor_type,
            "client_number": gateway_id,
            "sensor_id": sensor_id,
            "is_latest": True,
            "is_processed": False,
            "alarm_type": AlarmType.SENSOR_ALARM.value,
        }
        sensor_info = cls.get_sensor_info(sensor_id)
        if not sensor_info:
            logger.warning(
                f"can't get sensor_info in process sensor alarm :{sensor_id=}"
            )
            return
        parsed_dict.update(sensor_info)
        params = origin_data.get("params", {})
        battery_alert = params.get("battery_alert")
        online_alert = params.get("online_alert")
        if battery_alert:
            create_time = datetime_from_str(battery_alert["time"])
            alarm_level = int(battery_alert.get("battery_alertl", 0))
            parsed_dict["alarm_describe"] = "电池低电量报警"
            parsed_dict["is_online"] = True
        else:
            create_time = datetime_from_str(online_alert["time"])
            alarm_level = int(online_alert.get("online_alertl", 0))
            parsed_dict["alarm_describe"] = "掉线报警"
            parsed_dict["is_online"] = False
        parsed_dict["create_date"] = create_time
        parsed_dict["update_date"] = create_time
        if alarm_level == 1:
            parsed_dict["alarm_level"] = AlarmLevel.ALARM.value
        else:
            parsed_dict["alarm_level"] = AlarmLevel.NORMAL.value
        if parsed_dict["is_online"] is False:
            AlarmInfo.objects.filter(
                is_latest=True,
                sensor_id=sensor_id,
                alarm_type=AlarmType.POINT_ALARM.value,
            ).update(is_online=False)
            # set corresponding sensor_type db's is_online to false
            my_col = MONGO_CLIENT[sensor_type]
            my_query = {"is_latest": True, "sensor_id": sensor_id}
            new_values = {"$set": {"is_online": False}}
            my_col.update_one(my_query, new_values)
        new_alarm_info = AlarmInfo(**parsed_dict)
        new_alarm_info.save()
        # set unprocessed_unm for site
        normal_redis.incrby(f"{SITE_UNPROCESSED_NUM}{parsed_dict['site_id']}")
        # todo deal with ws
        return new_alarm_info

    @classmethod
    def can_precessing(cls, gateway_id: str, sensor_id: str) -> bool:
        sensor_info_key = f"{SENSOR_INFO_PREFIX}{sensor_id}"
        # 网关已启用且档案已配置才会入库
        return normal_redis.sismember("client_ids", gateway_id) and normal_redis.exists(
            sensor_info_key
        )

    @classmethod
    def get_sensor_info(cls, sensor_id: str) -> Optional[dict]:
        sensor_info_key = f"{SENSOR_INFO_PREFIX}{sensor_id}"
        data_from_redis = normal_redis.hgetall(sensor_info_key)
        if data_from_redis:
            return data_from_redis
        else:
            sensor_info = SensorConfigService(
                sensor_id
            ).get_or_set_sensor_info_from_sensor_config()
            if sensor_info is None:
                logger.warning(f"get sensor_info failed for {sensor_id=}")
            return sensor_info

    @classmethod
    def insert_and_update_alarm_info(cls, sensor_obj_dict: dict) -> Optional[dict]:
        sensor_id = sensor_obj_dict["sensor_id"]
        site_id = sensor_obj_dict["site_id"]
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
            "create_date": sensor_obj_dict["create_date"],
            "update_date": sensor_obj_dict["update_date"],
            "customer_id": sensor_obj_dict["customer_id"],
            "site_id": site_id,
            "equipment_id": sensor_obj_dict["equipment_id"],
            "point_id": sensor_obj_dict["point_id"],
        }
        # update is_latest filed to false
        AlarmInfo.objects.filter(
            is_latest=True, sensor_id=sensor_id, alarm_type=AlarmType.POINT_ALARM.value
        ).update(is_latest=False)
        new_alarm_info = AlarmInfo(**alarm_info)
        new_alarm_info.save()
        # set unprocessed_unm for site
        normal_redis.incrby(f"{SITE_UNPROCESSED_NUM}{str(site_id)}")
        return alarm_info

    @classmethod
    def insert_and_update_sensor_data(
        cls, sensor_type: str, gateway_id: str, sensor_id: str, sensor_data: dict
    ) -> Optional[dict]:
        """
        1. insert new sensor data to db;
        2. update old sensor data's is_latest to false
        """
        my_query = {"is_latest": True, "sensor_id": sensor_id}
        new_values = {"$set": {"is_latest": False}}
        try:
            parsed_sensor_dict = cls.parse_origin_sensor_data(
                sensor_type, gateway_id, sensor_id, sensor_data
            )
            if not parsed_sensor_dict:
                logger.warning(
                    "-----------------parsed_sensor_dict is none, discard this data"
                )
                return
            my_col = MONGO_CLIENT[sensor_type]
            # update old data before insert new sensor data
            my_col.update_many(my_query, new_values)
            # insert new sensor data
            my_col.insert_one(parsed_sensor_dict)
        except Exception as e:
            logger.error(f"***************insert new sensor data error with {e=}")
            return
        return parsed_sensor_dict

    @classmethod
    def parse_origin_sensor_data(
        cls, sensor_type: str, gateway_id: str, sensor_id: str, sensor_data: dict
    ) -> Optional[dict]:
        parsed_dict = {
            "_id": ObjectId(),
            "sensor_type": sensor_type,
            "client_number": gateway_id,
            "sensor_id": sensor_id,
            "is_latest": True,
            "is_online": True,
        }
        sensor_info = cls.get_sensor_info(sensor_id)
        if not sensor_info:
            logger.warning(f"can't get sensor_info in insert alarm data:{sensor_id=}")
            return
        parsed_dict.update(sensor_info)
        params = sensor_data.get("params", {})
        # if sensor_type in [SensorType.ae.value, SensorType.tev.value, SensorType.temp.value, SensorType.uhf.vale]:
        if sensor_type != SensorType.mech:
            parsed_dict.update(params.get("status", {}))
            parsed_dict.update(params.get("wparam", {}))
            data = params.get("data", {})
            create_time = datetime_from_str(data["acqtime"])
            parsed_dict["create_date"] = create_time
            parsed_dict["update_date"] = create_time
            parsed_dict["alarm_flag"] = data.get("alert_flag", AlarmFlag.NO_PUSH.value)
            parsed_dict["alarm_level"] = data.get(
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
            create_time = datetime_from_str(sensor_data["acqtime"])
            parsed_dict["create_date"] = create_time
            parsed_dict["update_date"] = create_time
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
    def deal_with_ws_data(cls, sensor_data: dict, alarm_data: dict):
        sensor_id = sensor_data["sensor_id"]
        # WsSensorDataSend(sensor_id).ws_send(sensor_data)

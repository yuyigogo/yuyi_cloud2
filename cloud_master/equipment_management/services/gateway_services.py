from collections import defaultdict
from datetime import datetime
from typing import Optional

from alarm_management.models.alarm_info import AlarmInfo
from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from equipment_management.models.gateway import GateWay
from equipment_management.models.sensor_config import SensorConfig
from mongoengine import Q

from common.const import SensorType
from common.framework.service import BaseService
from common.utils import get_objects_pagination


class GatewayService(BaseService):
    def __init__(self, site_id: str):
        self.site_id = site_id

    def create_gateway(self, data: dict) -> GateWay:
        gateway = GateWay(
            name=data["name"],
            customer=data["customer"],
            client_number=data["client_number"],
            time_adjusting=datetime.fromtimestamp(data["time_adjusting"]),
            site_id=self.site_id,
            remarks=data.get("remarks"),
        )
        gateway.save()
        return gateway

    def get_list_gateway_in_site(self) -> list:
        gateways = GateWay.objects.only("name", "client_number").filter(
            site_id=self.site_id
        )
        data, client_numbers = [], []
        for gateway in gateways:
            client_number = gateway.client_number
            client_numbers.append(client_number)
            data.append(
                {
                    "gateway_id": str(gateway.id),
                    "name": gateway.name,
                    "client_number": client_number,
                }
            )
        latest_info_dict = self.get_latest_gateway_infos(client_numbers)
        if latest_info_dict:
            [
                d.update(latest_info_dict.get(d["client_number"]))
                for d in data
                if latest_info_dict.get(d["client_number"])
            ]
        return data

    @classmethod
    def get_latest_gateway_infos(cls, client_numbers: list) -> dict:
        alarm_infos = AlarmInfo.objects.only(
            "is_online", "create_date", "client_number"
        ).filter(client_number__in=client_numbers, is_latest=True)
        return {
            alarm_info.client_number: {
                "is_online": alarm_info.is_online,
                "update_time": alarm_info.create_date,
            }
            for alarm_info in alarm_infos
        }

    @classmethod
    def get_sensor_info_in_gateway(
        cls,
        page: int,
        limit: int,
        client_number: str,
        sensor_id: Optional[str],
        sensor_type: Optional[str],
        is_online: Optional[bool],
    ) -> tuple:
        sensor_query = Q(client_number=client_number)
        if sensor_id:
            sensor_query &= Q(sensor_number=sensor_id)
        if sensor_type:
            sensor_query &= Q(sensor_type=sensor_type)
        if is_online is not None:
            # todo add join index in alarm_info?
            alarm_query = sensor_query & Q(is_online=is_online)
            sensor_ids = AlarmInfo.objects.filter(alarm_query).values_list("sensor_id")
            sensor_query &= Q(sensor_number__in=sensor_ids)
        sensors = SensorConfig.objects.only(
            "sensor_number", "sensor_type", "communication_mode", "client_number"
        ).filter(sensor_query)
        total = sensors.count()
        sensor_by_page = get_objects_pagination(page, limit, sensors)
        data, sensor_type_sensor_ids = [], defaultdict(list)
        for sensor_config in sensor_by_page:
            sensor_type = sensor_config.sensor_type
            sensor_id = sensor_config.sensor_number
            data.append(
                {
                    "name": f"{sensor_type}传感器",
                    "sensor_id": sensor_id,
                    "sensor_type": sensor_type,
                    "client_number": sensor_config.client_number,
                }
            )
            sensor_type_sensor_ids[sensor_type].append(sensor_id)
        sensor_infos = cls._get_sensor_info_in_gateway(sensor_type_sensor_ids)
        data = [
            info_dict.update(sensor_infos.get(info_dict["sensor_id"]))
            for info_dict in data
        ]
        return total, data

    @classmethod
    def _get_sensor_info_in_gateway(cls, sensor_type_sensor_ids: dict) -> dict:
        sensor_datas = []
        for sensor_type, sensor_ids in sensor_type_sensor_ids.items():
            not_display_fields = None
            my_col = MONGO_CLIENT[sensor_type]
            raw_query = {"sensor_id": {"$in": sensor_ids}, "is_latest": True}
            if sensor_type == SensorType.uhf.value:
                not_display_fields = {"prps": 0}
            sensors = my_col.find(raw_query, not_display_fields)
            sensor_datas.extend(sensors)
        sensor_infos = {
            sensor["sensor_id"]: {
                "sensor_data_id": str(sensor["_id"]),
                "update_time": bson_to_dict(sensor["create_date"]),
                "upload_interval": sensor.get("upload_interval", ""),
                "is_online": sensor["is_online"],
                "battery": sensor.get("battery", ""),
                "rssi": sensor.get("rssi", ""),
                "snr": sensor.get("snr", ""),
            }
            for sensor in sensor_datas
        }
        return sensor_infos

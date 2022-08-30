from collections import defaultdict
from typing import Optional, Tuple

from alarm_management.models.alarm_info import AlarmInfo
from bson import ObjectId
from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from mongoengine import Q, QuerySet

from common.const import AlarmType, SensorType
from common.framework.service import BaseService
from common.utils import get_objects_pagination


class SensorListService(BaseService):
    @classmethod
    def get_sensor_list_from_site_or_equipment(
        cls,
        page: int,
        limit: int,
        site_id: Optional[str] = None,
        equipment_id: Optional[str] = None,
        point_id: Optional[str] = None,
        alarm_level: Optional[int] = None,
        is_online: Optional[bool] = None,
        sensor_type: Optional[str] = None,
    ) -> tuple:
        assert (
            site_id or equipment_id
        ), "should have one value in site_id or equipment_id"
        alarm_info_query = Q(is_latest=True, alarm_type=AlarmType.POINT_ALARM.value)
        if site_id:
            alarm_info_query &= Q(site_id=site_id)
        else:
            alarm_info_query &= Q(equipment_id=equipment_id)
        if point_id:
            alarm_info_query &= Q(point_id=point_id)
        if alarm_level is not None:
            alarm_info_query &= Q(alarm_level=alarm_level)
        if is_online is not None:
            alarm_info_query &= Q(is_online=is_online)
        if sensor_type:
            alarm_info_query &= Q(sensor_type=sensor_type)
        alarm_infos = AlarmInfo.objects.filter(alarm_info_query)
        total = alarm_infos.count()
        alarm_infos_by_page = get_objects_pagination(
            page, limit, alarm_infos.order_by("-create_date")
        )
        data = cls.assemble_alarm_infos(alarm_infos_by_page)
        return total, data

    @classmethod
    def assemble_alarm_infos(cls, alarm_infos: QuerySet) -> list:
        alarm_id_data_id, equipment_ids, point_ids = {}, [], []
        sensor_type_data_ids = defaultdict(list)
        for alarm_info in alarm_infos:
            alarm_info_id = alarm_info.pk
            sensor_type = alarm_info.sensor_type
            sensor_data_id = alarm_info.sensor_data_id
            alarm_id_data_id[alarm_info_id] = sensor_data_id
            equipment_ids.append(alarm_info.equipment_id)
            point_ids.append(alarm_info.point_id)
            sensor_type_data_ids[sensor_type].append(sensor_data_id)
        equipment_id_name, point_id_name = cls.get_names_info(equipment_ids, point_ids)
        sensor_id_to_info = cls.get_sensor_data(
            sensor_type_data_ids, equipment_id_name, point_id_name
        )
        return [
            sensor_id_to_info.get(sensor_data_id)
            for _, sensor_data_id in alarm_id_data_id.items()
            if sensor_id_to_info.get(sensor_data_id)
        ]

    @classmethod
    def get_names_info(cls, equipment_ids: list, point_ids: list) -> Tuple[dict, dict]:
        equipment_id_name = dict(
            ElectricalEquipment.objects.filter(id__in=equipment_ids).values_list(
                "id", "device_name"
            )
        )
        point_id_name = dict(
            MeasurePoint.objects.filter(id__in=point_ids).values_list(
                "id", "measure_name"
            )
        )
        return equipment_id_name, point_id_name

    @classmethod
    def get_sensor_data(
        cls, sensor_type_id: dict, equipment_id_name: dict, point_id_name: dict
    ) -> dict:
        list_data = []
        for sensor_type, sensor_ids in sensor_type_id.items():
            not_display_fields = None
            my_col = MONGO_CLIENT[sensor_type]
            raw_query = {"_id": {"$in": sensor_ids}}
            if sensor_type == SensorType.uhf.value:
                not_display_fields = {"prps": 0}
            sensors = my_col.find(raw_query, not_display_fields)
            list_data.extend(sensors)
        sensor_id_dict = {}
        for sensor in list_data:
            sensor_obj_id = sensor["_id"]
            sensor_type = sensor["sensor_type"]
            equipment_id = sensor["equipment_id"]
            point_id = sensor["point_id"]
            info = {
                "sensor_data_id": str(sensor_obj_id),
                # "sensor_id": sensor["sensor_id"],
                "sensor_type": sensor_type,
                "equipment_id": equipment_id,
                "equipment_name": equipment_id_name.get(ObjectId(equipment_id), ""),
                "point_id": point_id,
                "point_name": point_id_name.get(ObjectId(point_id), ""),
                "is_online": sensor["is_online"],
                "upload_interval": sensor["upload_interval"],
                "update_time": bson_to_dict(sensor["create_date"]),
                "alarm_level": sensor["alarm_level"],
                "alarm_describe": sensor["alarm_describe"],
            }
            if sensor_type == SensorType.ae:
                info["character_value"] = sensor["maxvalue"]
                info["battery"] = sensor["battery"]
                info["rssi"] = sensor["rssi"]
                info["snr"] = sensor["snr"]
            elif sensor_type == SensorType.tev:
                info["character_value"] = sensor["amp"]
                info["battery"] = sensor["battery"]
                info["rssi"] = sensor["rssi"]
                info["snr"] = sensor["snr"]
            elif sensor_type == SensorType.uhf:
                info["character_value"] = sensor["ampmax"]
                info["battery"] = sensor["battery"]
                info["rssi"] = sensor["rssi"]
                info["snr"] = sensor["snr"]
            elif sensor_type == SensorType.temp:
                info["character_value"] = sensor["T"]
                info["battery"] = sensor["battery"]
            else:
                # mech
                # todo
                info["character_value"] = sensor["todo"]
            sensor_id_dict[sensor_obj_id] = info
        return sensor_id_dict

from datetime import datetime
from typing import Optional, Tuple

from alarm_management.models.alarm_info import AlarmInfo
from cloud.models import bson_to_dict
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from mongoengine import Q, QuerySet

from common.const import AlarmLevel
from common.framework.service import BaseService
from common.utils import get_objects_pagination


class AlarmListService(BaseService):
    def __init__(self, alarm_type: int):
        self.alarm_type = alarm_type

    def get_alarm_list_from_site_or_equipment(
        self,
        page: int,
        limit: int,
        site_id: Optional[str] = None,
        equipment_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        alarm_level: Optional[int] = None,
        is_processed: Optional[bool] = None,
        sensor_type: Optional[str] = None,
    ) -> tuple:
        alarm_info_query = Q(alarm_type=self.alarm_type)
        if site_id:
            alarm_info_query &= Q(site_id=site_id)
        else:
            alarm_info_query &= Q(equipment_id=equipment_id)
        if alarm_level is not None:
            alarm_info_query &= Q(alarm_level=alarm_level)
        else:
            alarm_info_query &= Q(alarm_level__in=AlarmLevel.abnormal_alarm_level())
        if start_date or end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            date_query = Q(create_date__gte=start_date) & Q(create_date__lte=end_date)
            alarm_info_query &= date_query
        if is_processed is not None:
            alarm_info_query &= Q(is_processed=is_processed)
        if sensor_type:
            alarm_info_query &= Q(sensor_type=sensor_type)
        alarm_infos = AlarmInfo.objects.filter(alarm_info_query)
        total = alarm_infos.count()
        alarm_infos_by_page = get_objects_pagination(
            page, limit, alarm_infos.order_by("-create_date")
        )
        data = self.assemble_alarm_list(alarm_infos_by_page)
        return total, data

    @classmethod
    def assemble_alarm_list(cls, alarm_infos: QuerySet) -> list:
        data, equipment_ids, point_ids = [], [], []
        for alarm_info in alarm_infos:
            equipment_id = alarm_info.equipment_id
            point_id = alarm_info.point_id
            equipment_ids.append(equipment_id)
            point_ids.append(point_ids)
            data.append(
                {
                    "sensor_data_id": str(alarm_info.sensor_data_id),
                    "sensor_type": alarm_info.sensor_type,
                    "equipment_id": str(equipment_id),
                    "point_id": str(point_id),
                    "is_processed": alarm_info.is_processed,
                    "update_time": bson_to_dict(alarm_info.create_date),
                    "alarm_level": alarm_info.alarm_level,
                    "alarm_describe": alarm_info.alarm_describe,
                    "processed_remarks": alarm_info.processed_remarks,
                }
            )
        equipment_id_name, point_id_name = cls.get_names_info(equipment_ids, point_ids)
        return [
            alarm_dict.update(
                {
                    "equipment_name": equipment_id_name.get(
                        alarm_dict["equipment_id"], ""
                    ),
                    "point_name": point_id_name.get(alarm_dict["point_id"], ""),
                }
            )
            for alarm_dict in data
        ]

    @classmethod
    def get_names_info(cls, equipment_ids: list, point_ids: list) -> Tuple[dict, dict]:
        equipments = ElectricalEquipment.objects.only("device_name").filter(
            id__in=equipment_ids
        )
        points = MeasurePoint.objects.only("measure_name").filter(id__in=point_ids)
        equipment_id_name = {str(e.pk): e.device_name for e in equipments}
        point_id_name = {str(p.pk): p.measure_name for p in points}
        return equipment_id_name, point_id_name

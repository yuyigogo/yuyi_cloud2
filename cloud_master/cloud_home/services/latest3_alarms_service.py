from functools import lru_cache

from alarm_management.models.alarm_info import AlarmInfo
from file_management.models.electrical_equipment import ElectricalEquipment
from mongoengine import Q
from sites.models.site import Site

from common.const import AlarmType
from common.framework.service import BaseService
from common.utils import get_objects_pagination


class LatestAlarmsService(BaseService):
    def __init__(self, user):
        self.user = user

    def get_latest3_alarms(self):
        query = Q(alarm_type=AlarmType.POINT_ALARM.value, is_latest=True)
        if self.user.is_cloud_or_client_super_admin():
            query = query
        elif self.user.is_normal_admin():
            query &= Q(customer_id=self.user.customer)
        else:
            query &= Q(site_id__in=self.user.sites)
        alarm_infos = AlarmInfo.objects.filter(query)
        alarm_infos_by_page = get_objects_pagination(
            1, 3, alarm_infos.order_by("-create_date")
        )
        site_ids, equipment_ids, data = [], [], []
        for alarm_info in alarm_infos_by_page:
            site_id = str(alarm_info.site_id)
            equipment_id = str(alarm_info.equipment_id)
            site_ids.append(site_id)
            equipment_ids.append(equipment_id)
            data.append(
                {
                    "site_id": site_id,
                    "equipment_id": equipment_id,
                    "is_processed": alarm_info.is_processed,
                    "alarm_level": alarm_info.alarm_level,
                    "sensor_type": alarm_info.sensor_type,
                    "sensor_id": alarm_info.sensor_id,
                    "alarm_id": str(alarm_info.pk),
                    "processed_remarks": alarm_info.processed_remarks,
                }
            )
        site_infos, equipment_infos = self.get_site_equipment_name(
            site_ids, equipment_ids
        )
        return [
            d.update(
                {
                    "site_name": site_infos.get(d["site_id"]),
                    "equipment_name": equipment_infos.get("equipment_id"),
                }
            )
            for d in data
        ]

    @classmethod
    @lru_cache
    def get_site_equipment_name(cls, site_ids: list, equipment_ids: list) -> tuple:
        site_infos = dict(
            Site.objects.filter(id__in=site_ids).values_list("id", "name")
        )
        equipment_infos = dict(
            ElectricalEquipment.objects.filter(id__in=equipment_ids).values_list(
                "id", "name"
            )
        )
        return site_infos, equipment_infos

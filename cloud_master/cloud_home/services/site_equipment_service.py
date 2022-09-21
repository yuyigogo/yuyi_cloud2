from collections import defaultdict
from typing import Union, Optional

from alarm_management.models.alarm_info import AlarmInfo
from bson import ObjectId
from file_management.models.electrical_equipment import ElectricalEquipment
from sites.models.site import Site

from common.const import AlarmLevel, AlarmType, ALL
from common.framework.service import BaseService


class SiteEquipmentService(BaseService):
    @classmethod
    def get_equipment_status_in_site(cls, site_id: Union[str, ObjectId]) -> list:
        equipments = ElectricalEquipment.objects.only("device_type").filter(
            site_id=site_id
        )
        equipment_type2_ids = defaultdict(list)
        for equipment in equipments:
            equipment_type2_ids[equipment.device_type].append(equipment.id)
        status_info = []
        for device_type, equipment_ids in equipment_type2_ids.items():
            status_dict = {
                "total": len(equipment_ids),
                "device_type": device_type,
                "alarm_num": 0,
                "warning_num": 0,
                "normal_num": 0,
            }
            alarm_infos = AlarmInfo.objects.only("equipment_id", "alarm_level").filter(
                equipment_id__in=equipment_ids,
                alarm_type=AlarmType.POINT_ALARM.value,
                is_latest=True,
            )
            equipment_id2_alarm_level = defaultdict(set)
            for alarm_info in alarm_infos:
                equipment_id2_alarm_level[alarm_info.equipment_id].add(
                    alarm_info.alarm_level
                )
            for equipment_id, alarm_levels in equipment_id2_alarm_level.items():
                if AlarmLevel.ALARM.value in alarm_levels:
                    status_dict["alarm_num"] += 1
                elif AlarmLevel.WARNING.value in alarm_levels:
                    status_dict["warning_num"] += 1
                else:
                    status_dict["normal_num"] += 1
            status_info.append(status_dict)
        return status_info

    @classmethod
    def get_top5_site_ids(cls, customer_id: Optional[str] = None) -> list:
        if customer_id is None:
            site_ids = list(Site.objects.filter(name__ne=ALL).values_list("id"))
        else:
            site_ids = list(Site.objects.filter(customer=customer_id).values_list("id"))
        aggregation = [
            {"$match": {"site_id": {"$in": site_ids}}},
            {
                "$group": {
                    "_id": {"site_id": "$site_id"},
                    "e_count": {"$sum": 1},
                }
            },
            {"$sort": {"e_count": -1}},
            {"$limit": 5},
        ]
        equipments = ElectricalEquipment.objects.aggregate(*aggregation)
        return [e["_id"]["site_id"] for e in equipments]

    @classmethod
    def get_sites_status(cls, site_ids: list) -> list:
        site_id2_name = dict(Site.objects.filter(id__in=site_ids).values_list("id", "name"))
        equipments = ElectricalEquipment.objects.only("site_id").filter(site_id__in=site_ids)
        site_id2_equipment_ids = defaultdict(set)
        for e in equipments:
            site_id2_equipment_ids[e.site_id].add(e.id)
        status_info = []
        for site_id, equipment_ids in site_id2_equipment_ids.items():
            status_dict = {
                "total": len(equipment_ids),
                "site_name": site_id2_name.get(site_id),
                "alarm_num": 0,
                "warning_num": 0,
                "normal_num": 0,
            }
            alarm_infos = AlarmInfo.objects.only("equipment_id", "alarm_level").filter(
                equipment_id__in=equipment_ids,
                alarm_type=AlarmType.POINT_ALARM.value,
                is_latest=True,
            )
            equipment_id2_alarm_level = defaultdict(set)
            for alarm_info in alarm_infos:
                equipment_id2_alarm_level[alarm_info.equipment_id].add(
                    alarm_info.alarm_level
                )
            for equipment_id, alarm_levels in equipment_id2_alarm_level.items():
                if AlarmLevel.ALARM.value in alarm_levels:
                    status_dict["alarm_num"] += 1
                elif AlarmLevel.WARNING.value in alarm_levels:
                    status_dict["warning_num"] += 1
                else:
                    status_dict["normal_num"] += 1
            status_info.append(status_dict)
        return status_info

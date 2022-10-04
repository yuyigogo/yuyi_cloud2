import logging
from collections import defaultdict
from typing import Optional

from alarm_management.models.alarm_info import AlarmInfo
from bson import ObjectId
from cloud.settings import MONGO_CLIENT
from cloud_home.models.status_statistics import CStatusStatistic, SStatusStatistic
from customer.models.customer import Customer
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from mongoengine import DoesNotExist
from sites.models.site import Site

from common.const import ALL, AlarmLevel, AlarmType, SensorType
from common.framework.service import BaseService

logger = logging.getLogger(__name__)


class StatusStatisticService(BaseService):
    def __init__(
        self,
        customer_id: Optional[str] = None,
        site_id: Optional[str] = None,
    ):
        assert customer_id or site_id, "StatusStatisticService init error"
        self.customer_id = customer_id
        self.site_id = site_id
        if self.customer_id:
            self.named_all_customer_id = str(Customer.objects.get(name=ALL).pk)
            self.is_named_all = customer_id == self.named_all_customer_id

    def get_customer_asset_info(self) -> dict:
        asset_info = {}
        if self.is_named_all:
            asset_info["site_num"] = Site.objects().count() - 1
            asset_info["equipment_num"] = ElectricalEquipment.objects().count()
            point_num = MeasurePoint.objects().count()
        else:
            sites = Site.objects.filter(customer=self.customer_id)
            site_ids = sites.values_list("id")
            asset_info["site_num"] = sites.count()
            equipments = ElectricalEquipment.objects.filter(site_id__in=site_ids)
            equipment_ids = equipments.values_list("id")
            asset_info["equipment_num"] = equipments.count()
            point_num = MeasurePoint.objects(equipment_id__in=equipment_ids).count()
        asset_info["point_num"] = point_num
        asset_info["sensor_num"] = point_num
        return asset_info

    def get_site_asset_info(self) -> dict:
        equipments = ElectricalEquipment.objects.filter(site_id=self.site_id)
        equipment_ids = equipments.values_list("id")
        asset_info = {"equipment_num": equipments.count()}
        point_num = MeasurePoint.objects(equipment_id__in=equipment_ids).count()
        asset_info["point_num"] = point_num
        asset_info["sensor_num"] = point_num
        return asset_info

    def get_site_equipment_status_statistics_in_site(self) -> list:
        equipments = ElectricalEquipment.objects.only("device_type").filter(
            site_id=self.site_id
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

    def get_top5_site_ids(self) -> list:
        if self.is_named_all:
            site_ids = list(
                Site.objects.filter(
                    customer__ne=self.named_all_customer_id
                ).values_list("id")
            )
        else:
            site_ids = list(
                Site.objects.filter(customer=self.customer_id).values_list("id")
            )
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
    def _get_customer_status_statistics(cls, site_ids: list) -> list:
        site_id2_name = dict(
            Site.objects.filter(id__in=site_ids).values_list("id", "name")
        )
        equipments = ElectricalEquipment.objects.only("site_id").filter(
            site_id__in=site_ids
        )
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

    def get_customer_equipment_status_statistics(self) -> list:
        site_ids = self.get_top5_site_ids()
        return self._get_customer_status_statistics(site_ids)

    def get_customer_or_site_sensor_online_ratio(self) -> list:
        match_query = {"is_latest": True}
        if self.site_id:
            # site sensor_online_ratio
            match_query.update({"site_id": self.site_id})
        else:
            # customer sensor_online_ratio
            if not self.is_named_all:
                match_query.update({"customer_id": self.customer_id})
        online_ratios = []
        for sensor_type in SensorType.values():
            my_col = MONGO_CLIENT[sensor_type]
            total = my_col.count_documents(match_query)
            if total == 0:
                continue
            match_query.update({"is_online": False})
            off_line = my_col.count_documents(match_query)
            online_ratios.append({sensor_type: round(1 - float(off_line / total))})
        return online_ratios

    def get_customer_or_site_point_distribution_info(self) -> list:
        match_query = {"is_latest": True, "alarm_type": AlarmType.POINT_ALARM.value}
        if self.site_id:
            match_query.update({"site_id": ObjectId(self.site_id)})
        else:
            if not self.is_named_all:
                match_query.update({"customer_id": ObjectId(self.customer_id)})
        aggregation = [
            {"$match": match_query},
            {
                "$group": {
                    "_id": {
                        "sensor_type": "$sensor_type",
                        "alarm_level": "$alarm_level",
                    },
                    "s_count": {"$sum": 1},
                }
            },
        ]
        alarm_infos = AlarmInfo.objects.aggregate(*aggregation)
        point_distribution_dict = defaultdict(dict)
        for alarm_info in alarm_infos:
            sensor_type = alarm_info["_id"]["sensor_type"]
            alarm_level = alarm_info["_id"]["alarm_level"]
            s_count = alarm_info["s_count"]
            d = {"sensor_type": sensor_type}
            if alarm_level == AlarmLevel.NORMAL:
                d["normal_num"] = s_count
            elif alarm_level == AlarmLevel.WARNING:
                d["warning_num"] = s_count
            else:
                d["alarm_num"] = s_count
            point_distribution_dict[sensor_type].update(d)
        return list(point_distribution_dict.values())

    def get_customer_or_site_equipment_abnormal_ratio(self) -> float:
        if self.site_id:
            site_ids = [self.site_id]
        else:
            if not self.is_named_all:
                site_ids = Site.objects.filter(customer=self.customer_id).values_list(
                    "id"
                )
            else:
                site_ids = Site.objects.filter(
                    customer__ne=self.named_all_customer_id
                ).values_list("id")
        equipment_ids = ElectricalEquipment.objects.filter(
            site_id__in=site_ids
        ).values_list("id")
        total = len(equipment_ids)
        if total == 0:
            return float(0)
        abnormal_num = 0
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
            if (
                AlarmLevel.ALARM.value in alarm_levels
                or AlarmLevel.WARNING.value in alarm_levels
            ):
                abnormal_num += 1
        return round(float(abnormal_num / total))


class StatusStatisticApiService(StatusStatisticService):
    def __init__(
        self,
        is_refresh: bool,
        customer_id: Optional[str] = None,
        site_id: Optional[str] = None,
    ):
        self.is_refresh = is_refresh
        super().__init__(customer_id, site_id)

    def get_customer_or_site_status_infos(self) -> dict:
        if self.is_refresh is False:
            infos = self.get_customer_or_site_status_infos_from_cache()
        else:
            infos = self._get_customer_or_site_status_infos()
        return infos

    def get_customer_or_site_status_infos_from_cache(self) -> Optional[dict]:
        try:
            if self.customer_id:
                status_statistic = CStatusStatistic.objects.get(
                    customer_id=self.customer_id
                )
            else:
                status_statistic = SStatusStatistic.objects.get(site_id=self.site_id)
        except DoesNotExist:
            logger.warning(f"can't get {self.customer_id}'s customer_status_infos")
            return
        return {
            "asset_info": status_statistic.asset_info,
            "equipment_status_info": status_statistic.equipment_status_info,
            "sensor_online_ratio": status_statistic.sensor_online_ratio,
            "point_distribution_info": status_statistic.point_distribution_info,
        }

    def _get_customer_or_site_status_infos(self) -> dict:
        """
        get one customer/site's status infos, it should not be the named all customer or site
        """
        if self.customer_id:
            asset_info = self.get_customer_asset_info()
            equipment_status_info = self.get_customer_equipment_status_statistics()
            sensor_online_ratio = self.get_customer_or_site_sensor_online_ratio()
            point_distribution_info = (
                self.get_customer_or_site_point_distribution_info()
            )
        else:
            asset_info = self.get_site_asset_info()
            equipment_status_info = self.get_site_equipment_status_statistics_in_site()
            sensor_online_ratio = self.get_customer_or_site_sensor_online_ratio()
            point_distribution_info = (
                self.get_customer_or_site_point_distribution_info()
            )
        infos = {
            "asset_info": asset_info,
            "equipment_status_info": equipment_status_info,
            "sensor_online_ratio": sensor_online_ratio,
            "point_distribution_info": point_distribution_info,
        }
        if self.customer_id:
            # update the customer's c_status_statistic
            CStatusStatistic.objects.filter(customer_id=self.customer_id).update(
                **infos
            )
        else:
            # update the site's c_status_statistic
            SStatusStatistic.objects.filter(site_id=self.site_id).update(**infos)
        return infos

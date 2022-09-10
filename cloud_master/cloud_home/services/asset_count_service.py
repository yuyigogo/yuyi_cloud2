from typing import Optional

from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint
from sites.models.site import Site

from common.framework.service import BaseService


class AssetCountService(BaseService):
    @classmethod
    def get_customer_assets(cls, customer_id: Optional[str] = None) -> dict:
        asset_infos = {}
        if customer_id is None:
            asset_infos["site_num"] = Site.objects().count() - 1
            asset_infos["equipment_num"] = ElectricalEquipment.objects().count()
            point_num = MeasurePoint.objects().count()
        else:
            sites = Site.objects.filter(customer=customer_id)
            site_ids = sites.values_list("id")
            asset_infos["site_num"] = sites.count()
            equipments = ElectricalEquipment.objects.filter(site_id__in=site_ids)
            equipment_ids = equipments.values_list("id")
            asset_infos["equipment_num"] = equipments.count()
            point_num = MeasurePoint.objects(equipment_id__in=equipment_ids).count()
        asset_infos["point_num"] = point_num
        asset_infos["sensor_num"] = point_num
        return asset_infos

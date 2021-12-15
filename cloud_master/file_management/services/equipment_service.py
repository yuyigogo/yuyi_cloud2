from collections import defaultdict
from typing import Union

from bson import ObjectId

from common.framework.service import BaseService
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint


class EquipmentService(BaseService):
    def __init__(self, site_id: Union[str, ObjectId]):
        self.site_id = site_id

    def create_new_equipment(self, data: dict) -> ElectricalEquipment:
        equipment = ElectricalEquipment(
            site_id=self.site_id,
            device_name=data["device_name"],
            device_type=data["device_type"],
            voltage_level=data["voltage_level"],
            operation_number=data.get("operation_number"),
            asset_number=data.get("asset_number"),
            device_model=data.get("device_model"),
            factory_number=data.get("factory_number"),
            remarks=data.get("remarks"),
        )
        equipment.save()
        return equipment

    def get_equipments_for_site(self):
        equipments = ElectricalEquipment.objects.filter(site_id=self.site_id)
        return [
            {
                "device_name": e.device_name,
                "device_type": e.device_type,
                "voltage_level": e.voltage_level,
                "operation_number": e.operation_number,
                "asset_number": e.asset_number,
                "device_model": e.device_model,
                "factory_number": e.factory_number,
                "remarks": e.remarks,
                "site_id": str(self.site_id),
            }
            for e in equipments
        ]

    @classmethod
    def delete_equipment(cls, equipment_id: Union[str, ObjectId], clear_resource=False):
        points = MeasurePoint.objects(equipment_id=equipment_id)
        if clear_resource:
            # todo delete sensor data
            sensor_dict = defaultdict(list)
            for p in points:
                sensor_dict[p.measure_type].append(p.sensor_number)
        points.delete()
        ElectricalEquipment.objects(id=equipment_id).delete()

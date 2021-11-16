from cloud.settings import MONGO_CLIENT
from common.framework.service import BaseService
from file_management.models.electrical_equipment import ElectricalEquipment
from file_management.models.measure_point import MeasurePoint


class SiteNavigationService(BaseService):
    @classmethod
    def get_latest_sensor_info(cls, sensor_number: str, sensor_type: str) -> dict:
        mongo_col = MONGO_CLIENT[sensor_type]
        sensor_data = mongo_col.find_one({"sensor_id": sensor_number, "is_new": True})
        return sensor_data if sensor_data else {}

    @classmethod
    def get_all_points_in_equipment(cls, equipment: ElectricalEquipment) -> list:
        points = MeasurePoint.objects.filter(equipment_id=equipment.pk)
        point_info = []
        for point in points:
            sensor_number = point.sensor_number
            sensor_type = point.measure_type
            point_info.append(
                {
                    "device_name": equipment.device_name,
                    "device_id": str(equipment.pk),
                    "measure_name": point.measure_name,
                    "measure_id": str(point.pk),
                    "sensor_type": sensor_type,
                    "sensor_number": sensor_number,
                    "sensor_info": cls.get_latest_sensor_info(
                        sensor_number, sensor_type
                    ),
                }
            )
        return point_info

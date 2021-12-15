from typing import Union

from bson import ObjectId
from cloud.settings import MONGO_CLIENT
from file_management.models.measure_point import MeasurePoint

from common.framework.service import BaseService


class MeasurePointService(BaseService):
    def __init__(self, equipment_id: Union[str, ObjectId]):
        self.equipment_id = equipment_id

    def create_new_measure_point(self, data: dict) -> MeasurePoint:
        measure_point = MeasurePoint(
            equipment_id=self.equipment_id,
            measure_name=data["measure_name"],
            measure_type=data["measure_type"],
            sensor_number=data["sensor_number"],
            remarks=data.get("remarks"),
        )
        measure_point.save()
        return measure_point

    def get_points_for_equipment(self):
        measure_points = MeasurePoint.objects.filter(equipment_id=self.equipment_id)
        return [
            {
                "measure_name": mp.measure_name,
                "measure_type": mp.measure_type,
                "sensor_number": mp.operation_number,
                "remarks": mp.remarks,
                "equipment_id": str(self.equipment_id),
            }
            for mp in measure_points
        ]

    @classmethod
    def delete_point(cls, point_id, clear_resource=False):
        point = MeasurePoint.objects.get(id=point_id)
        if clear_resource:
            mongo_col = MONGO_CLIENT[point.measure_type.lower()]
            mongo_col.delete_many({"sensor_id": point.sensor_number})
        point.delete()

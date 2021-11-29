from datetime import datetime

from cloud.settings import MONGO_CLIENT
from file_management.models.measure_point import MeasurePoint

from common.const import SensorType
from common.framework.service import BaseService


class PointsTrendService(BaseService):
    @classmethod
    def get_points_trend_data(
        cls, point_ids: list, start_date: str, end_date: str
    ) -> list:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        points = MeasurePoint.objects.only("sensor_number", "measure_type").filter(
            pk__in=point_ids
        )
        point_to_sensor = {
            str(point.pk): (point.sensor_number, point.measure_type) for point in points
        }
        data = []
        for point_id, (sensor_number, sensor_type) in point_to_sensor.items():
            mongo_col = MONGO_CLIENT[sensor_type]
            sensors = mongo_col.find(
                {
                    "sensor_id": sensor_number,
                    "create_time": {"$gte": start_date, "$lte": end_date},
                },
                {
                    "sensor_id": 1,
                    "sensor_type": 1,
                    "create_time": 1,
                    "params": 1,
                },
            )
            sensor_list = cls.assemble_sensor_data(sensors)
            data.append({point_id: sensor_list})
        return data

    @classmethod
    def assemble_sensor_data(cls, sensors):
        sensor_list = []
        for sensor in sensors:
            sensor_type = sensor["sensor_type"]
            if sensor_type == SensorType.temp:
                parm_key = sensor_type.capitalize()
            else:
                parm_key = sensor_type.upper()
            sensor_dict = {
                "id": str(sensor["_id"]),
                "sensor_id": sensor["sensor_id"],
                "sensor_type": sensor_type,
                "create_time": sensor["create_time"],
            }
            sensor_dict.update(sensor["params"][parm_key])
            sensor_list.append(sensor_dict)
        return sensor_list

from datetime import datetime, timedelta

from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from file_management.models.measure_point import MeasurePoint

from common.const import SensorType
from common.framework.service import BaseService


class PointsTrendService(BaseService):
    @classmethod
    def get_points_trend_data(
        cls, point_ids: list, start_date: str, end_date: str
    ) -> list:
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        points = MeasurePoint.objects.only(
            "sensor_number", "measure_type", "measure_name"
        ).filter(pk__in=point_ids)
        point_to_sensor = {
            str(point.pk): (point.sensor_number, point.measure_type, point.measure_name)
            for point in points
        }
        data = []
        for (
            point_id,
            (sensor_number, sensor_type, measure_name),
        ) in point_to_sensor.items():
            mongo_col = MONGO_CLIENT[sensor_type]
            if sensor_type == SensorType.uhf.value:
                display_fields = {
                    "sensor_id": 1,
                    "sensor_type": 1,
                    "create_time": 1,
                    f"params.{sensor_type.upper()}.ampmax": 1,
                    f"params.{sensor_type.upper()}.ampmean": 1,
                }
            else:
                display_fields = {
                    "sensor_id": 1,
                    "sensor_type": 1,
                    "create_time": 1,
                    "params": 1,
                }
            sensors = mongo_col.find(
                {
                    "sensor_id": sensor_number,
                    "create_time": {"$gte": start_date, "$lte": end_date},
                },
                display_fields,
            )
            sensor_list = cls.assemble_sensor_data(sensors)
            data.append(
                {
                    "point_id": point_id,
                    "measure_name": measure_name,
                    "point_data": sensor_list,
                }
            )
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
                "sensor_id": sensor["sensor_id"],
                "sensor_type": sensor_type,
                "create_time": bson_to_dict(sensor["create_time"]),
            }
            sensor_dict.update(sensor["params"][parm_key])
            sensor_list.append(sensor_dict)
        return sensor_list

    @classmethod
    def get_point_graph_data_on_certain_time(
        cls, point_ids: list, start_date: str
    ) -> list:
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = start_date + timedelta(days=1)
        points = MeasurePoint.objects.only(
            "sensor_number", "measure_type", "measure_name"
        ).filter(pk__in=point_ids)
        data = []
        for point in points:
            sensor_id = point.sensor_number
            sensor_type = point.measure_type
            mongo_col = MONGO_CLIENT[sensor_type]
            sensor = mongo_col.find_one(
                {
                    "sensor_id": sensor_id,
                    "create_time": {"$gte": start_date, "$lt": end_date},
                },
                {"create_time": 1, "params": 1, "_id": 0},
            )
            if sensor:
                data.append(
                    {
                        "measure_id": str(point.id),
                        "measure_name": point.measure_name,
                        "sensor_type": sensor_type,
                        "sensor_number": point.sensor_number,
                        "sensor_info": bson_to_dict(sensor),
                    }
                )
        return data

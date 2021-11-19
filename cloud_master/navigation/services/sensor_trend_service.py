from datetime import datetime

from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from common.framework.service import BaseService


class SensorTrendService(BaseService):
    @classmethod
    def get_sensor_trend_data(cls, sensor_list: list, start_date: str, end_date: str) -> dict:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        tmp = {}
        for sensor in sensor_list:
            sensor_id = sensor.get('sensor_id', '')
            sensor_type = sensor.get('sensor_type', '')
            if sensor_type in tmp:
                tmp[sensor_type].append(sensor_id)
            else:
                tmp[sensor_type] = [sensor_id]
        res = []
        for sensor_type, sensor_id_list in tmp.items():
            mongo_col = MONGO_CLIENT[sensor_type]
            sensor_data = mongo_col.find(
                {
                    "sensor_id": {"$in": sensor_id_list},
                    "create_time": {"$gte": start_date, "$lte": end_date}
                }
            )
            for _ in sensor_data:
                res.append(_)
        return bson_to_dict(res)


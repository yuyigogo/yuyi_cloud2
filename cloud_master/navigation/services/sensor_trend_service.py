from collections import defaultdict
from datetime import datetime

from cloud.models import bson_to_dict
from cloud.settings import MONGO_CLIENT
from common.framework.service import BaseService


class SensorTrendService(BaseService):
    @classmethod
    def get_sensor_trend_data(cls, sensor_list: list, start_date: str, end_date: str) -> dict:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        sensor_type_dict = defaultdict(list)
        for sensor in sensor_list:
            sensor_id = sensor.get('sensor_id', '')
            sensor_type = sensor.get('sensor_type', '')
            sensor_type_dict[sensor_type].append(sensor_id)
        res = defaultdict(list)
        for sensor_type, sensor_id_list in sensor_type_dict.items():
            mongo_col = MONGO_CLIENT[sensor_type]
            sensor_data = mongo_col.find(
                {
                    "sensor_id": {"$in": sensor_id_list},
                    "create_time": {"$gte": start_date, "$lte": end_date}
                }
            )
            res[sensor_type] = [_ for _ in sensor_data]
        return bson_to_dict(res)

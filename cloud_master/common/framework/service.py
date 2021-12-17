import logging
from collections import defaultdict

from cloud.settings import MONGO_CLIENT

logger = logging.getLogger(__name__)


class BaseService(object):
    """
    All service should inherit this class.
    """

    @classmethod
    def delete_points(cls, points, clear_resource=False):
        if clear_resource:
            sensor_dict = defaultdict(list)
            for point in points:
                sensor_dict[point.measure_type].append(point.sensor_number)
            cls.delete_sensor_data(sensor_dict)
        points.delete()

    @classmethod
    def delete_sensor_data(cls, sensor_dict: dict):
        # todo delete Sensor model
        for sensor_type, sensor_ids in sensor_dict.items():
            try:
                mongo_col = MONGO_CLIENT[sensor_type]
                mongo_col.delete_many({"sensor_id": {"$in": sensor_ids}})
            except Exception as e:
                logger.error(
                    f"delete sensor data failed with {sensor_type}- {sensor_ids} - {e=}"
                )

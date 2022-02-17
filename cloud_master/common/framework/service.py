import logging
from collections import defaultdict

from cloud.models import bson_to_dict
from cloud.settings import CLIENT_IDS, MONGO_CLIENT
from equipment_management.models.gateway import GateWay

from common.const import SensorType
from common.storage.redis import redis

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
        # todo clear client_ids in redis when delete customer or sites
        for sensor_type, sensor_ids in sensor_dict.items():
            try:
                mongo_col = MONGO_CLIENT[sensor_type]
                mongo_col.delete_many({"sensor_id": {"$in": sensor_ids}})
            except Exception as e:
                logger.error(
                    f"delete sensor data failed with {sensor_type=}- sensor_ids: {sensor_ids} - {e=}"
                )

    @classmethod
    def delete_sensor_data_from_gateway(cls, gateway: GateWay, clear_resource=False):
        client_id = gateway.client_number
        if clear_resource:
            for sensor_type in SensorType.values():
                try:
                    mongo_col = MONGO_CLIENT[sensor_type]
                    mongo_col.delete_many({"client_id": client_id})
                except Exception as e:
                    logger.error(
                        f"delete sensor data failed with {sensor_type=}- client_id: {client_id} - {e=}"
                    )
        gateway.delete()
        cls.remove_client_id_from_redis(client_id)

    @classmethod
    def remove_client_id_from_redis(cls, client_id: str):
        redis.srem(CLIENT_IDS, client_id)

    @classmethod
    def get_latest_sensor_info(cls, sensor_number: str, sensor_type: str) -> dict:
        mongo_col = MONGO_CLIENT[sensor_type]
        sensor_data = mongo_col.find_one({"sensor_id": sensor_number, "is_new": True},)
        return bson_to_dict(sensor_data) if sensor_data else {}

import logging
from functools import lru_cache
from typing import Optional

from cloud.models import bson_to_dict
from cloud.settings import CLIENT_IDS, MONGO_CLIENT
from equipment_management.models.gateway import GateWay
from equipment_management.models.sensor_config import SensorConfig

from common.const import SENSOR_INFO_PREFIX, SensorType
from common.storage.redis import redis

logger = logging.getLogger(__name__)


class BaseService(object):
    """
    All service should inherit this class.
    """

    @classmethod
    def delete_points(cls, points, clear_resource=False):
        deleted_sensor_numbers = points.values_list("sensor_number")
        SensorConfigService.delete_sensor_config_resource(deleted_sensor_numbers)
        points.delete()
        if clear_resource:
            cls.delete_sensor_data(deleted_sensor_numbers)

    @classmethod
    def delete_sensor_data(cls, deleted_sensor_numbers: list):
        """
        sensor data: sensor model(TEV, AE...); alarm_info
        """
        delete_filters = {"sensor_id": {"$in": deleted_sensor_numbers}}
        alarm_info_col = MONGO_CLIENT["alarm_info"]
        try:
            alarm_info_col.delete_many(delete_filters)
        except Exception as e:
            logger.error(
                f"delete alarm_info failed with {e=} for {deleted_sensor_numbers=}"
            )
        for sensor_type in SensorType.values():
            try:
                mongo_col = MONGO_CLIENT[sensor_type]
                mongo_col.delete_many(delete_filters)
            except Exception as e:
                logger.error(
                    f"delete sensor data failed with {sensor_type=}- sensor_ids: {deleted_sensor_numbers} - {e=}"
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
        sensor_data = mongo_col.find_one(
            {"sensor_id": sensor_number, "is_latest": True},
        )
        return bson_to_dict(sensor_data) if sensor_data else {}


class SensorConfigService(BaseService):
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id
        self.sensor_info_key = f"{SENSOR_INFO_PREFIX}{sensor_id}"

    def create_or_update_sensor_config_in_excel(
        self,
        customer_id: str,
        site_id: str,
        equipment_id: str,
        point_id: str,
        sensor_type: str,
    ):
        """
        when create file resource from excel, should create/update sensor_config,
        meanwhile should add sensor info to redis
        """
        sensor_config = SensorConfig.objects(sensor_number=self.sensor_id).first()
        if sensor_config:
            sensor_config.update(
                set__customer_id=customer_id,
                set__site_id=site_id,
                set__equipment_id=equipment_id,
                set__point_id=point_id,
                set__sensor_type=sensor_type,
            )
        else:
            sensor_config = SensorConfig(
                customer_id=customer_id,
                site_id=site_id,
                equipment_id=equipment_id,
                point_id=point_id,
                sensor_number=self.sensor_id,
                sensor_type=sensor_type,
            )
            sensor_config.save()
        # set sensor_info to redis
        self.set_sensor_info_to_redis(customer_id, site_id, equipment_id, point_id)

    def set_sensor_info_to_redis(
        self, customer_id: str, site_id: str, equipment_id: str, point_id: str,
    ):
        value = {
            "customer_id": customer_id,
            "site_id": site_id,
            "equipment_id": equipment_id,
            "point_id": point_id,
        }
        logger.info(f"set sensor_info to redis, key:{self.sensor_info_key}, {value=}")
        redis.hmset(self.sensor_info_key, value)

    def update_and_set_sensor_info(
        self,
        old_sensor_id: str,
        customer_id: str,
        site_id: str,
        equipment_id: str,
        point_id: str,
    ):
        """
        when the point's sensor_number has changed, the following things should to do:
            1. update sensor_config's sensor_number filed;
            2. before set new sensor_info to redis, should delete the old sensor_info
        """
        SensorConfig.objects.filter(sensor_number=old_sensor_id).update(
            sensor_number=self.sensor_id
        )
        old_sensor_info_key = f"{SENSOR_INFO_PREFIX}{old_sensor_id}"
        logger.info(f"delete {old_sensor_info_key} from redis")
        redis.delete(old_sensor_info_key)
        self.set_sensor_info_to_redis(customer_id, site_id, equipment_id, point_id)

    @classmethod
    def delete_sensor_config_resource(cls, sensor_ids: list):
        """
        when delete point, should delete the corresponding sensor_config and sensor_info in redis
        """
        SensorConfig.objects.filter(sensor_number__in=sensor_ids).delete()
        delete_sensor_info_keys = [
            f"{SENSOR_INFO_PREFIX}{sensor_id}" for sensor_id in sensor_ids
        ]
        for d_key in delete_sensor_info_keys:
            redis.delete(d_key)

    @lru_cache
    def get_sensor_info_from_sensor_config(self) -> Optional[dict]:
        try:
            sensor_config = SensorConfig.objects.only(
                "customer_id", "site_id", "equipment_id", "point_id"
            ).get(sensor_number=self.sensor_id)
        except Exception as e:
            logger.warning(f"get sensor_info failed for {self.sensor_id=} with {e=}")
            return
        customer_id = sensor_config.customer_id
        site_id = sensor_config.site_id
        equipment_id = sensor_config.equipment_id
        point_id = sensor_config.point_id
        self.set_sensor_info_to_redis(customer_id, site_id, equipment_id, point_id)
        return {
            "customer_id": customer_id,
            "site_id": site_id,
            "equipment_id": equipment_id,
            "point_id": point_id,
        }

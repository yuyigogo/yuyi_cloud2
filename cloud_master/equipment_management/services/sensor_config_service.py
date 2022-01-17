import logging

from equipment_management.models.sensor_config import SensorConfig

from common.const import SensorType
from common.framework.service import BaseService

logger = logging.getLogger(__name__)


class SensorConfigService(BaseService):
    def __init__(self, client_number: str):
        self.client_number = client_number

    def bulk_insert_sensor_configs(self, sensor_info: set):
        logger.info(
            f"bulk_insert_sensor_configs for {self.client_number=} with data: {sensor_info}"
        )
        sensor_configs = []
        for (sensor_id, sensor_type) in sensor_info:
            if sensor_type == SensorType.ae_and_tev():
                sensor_configs.append(
                    self.create_sensor_config_instance(
                        f"{SensorType.ae.value}传感器", sensor_id, SensorType.ae.value,
                    )
                )
                sensor_configs.append(
                    self.create_sensor_config_instance(
                        f"{SensorType.tev.value}传感器", sensor_id, SensorType.tev.value,
                    )
                )
            sensor_name = f"{sensor_type}传感器"
            sensor_configs.append(
                self.create_sensor_config_instance(sensor_name, sensor_id, sensor_type)
            )
        SensorConfig.objects.insert(sensor_configs)

    def create_sensor_config_instance(
        self, sensor_name: str, sensor_number: str, sensor_type: str
    ) -> SensorConfig:
        return SensorConfig(
            name=sensor_name,
            sensor_number=sensor_number,
            sensor_type=sensor_type,
            client_number=self.client_number,
        )

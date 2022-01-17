from datetime import datetime
from typing import Optional

from equipment_management.models.gateway import GateWay
from equipment_management.models.sensor_config import SensorConfig
from mongoengine import Q

from common.framework.service import BaseService
from common.utils import get_objects_pagination


class GatewayService(BaseService):
    def __init__(self, site_id: str):
        self.site_id = site_id

    def create_gateway(self, data: dict) -> GateWay:
        gateway = GateWay(
            name=data["name"],
            customer=data["customer"],
            client_number=data["client_number"],
            time_adjusting=datetime.fromtimestamp(data["time_adjusting"]),
            site_id=self.site_id,
            remarks=data.get("remarks"),
        )
        gateway.save()
        return gateway

    def get_list_gateway_in_site(self):
        gateways = GateWay.objects.only("name", "client_number").filter(
            site_id=self.site_id
        )
        return [
            {
                "gateway_id": str(gateway.id),
                "name": gateway.name,
                "client_number": gateway.client_number,
            }
            for gateway in gateways
        ]

    @classmethod
    def get_sensor_info_in_gateway(
        cls,
        page: int,
        limit: int,
        client_number: str,
        sensor_name: Optional[str],
        sensor_id: Optional[str],
        sensor_type: Optional[str],
    ) -> tuple:
        sensor_query = Q(client_number=client_number)
        if sensor_id:
            sensor_query = sensor_query & Q(sensor_number=sensor_id)
        if sensor_type:
            sensor_query = sensor_query & Q(sensor_type=sensor_type)
        if sensor_name:
            sensor_query = sensor_query & Q(name=sensor_name)
        sensors = SensorConfig.objects.only(
            "name", "sensor_number", "sensor_type"
        ).filter(sensor_query)
        total = sensors.count()
        sensor_by_page = get_objects_pagination(page, limit, sensors)
        data = []
        for sensor_config in sensor_by_page:
            data.append(
                {
                    "name": sensor_config.name,
                    "sensor_id": sensor_config.sensor_number,
                    "sensor_type": sensor_config.sensor_type,
                    "sensor_info": cls.get_latest_sensor_info(
                        sensor_config.sensor_number, sensor_config.sensor_type
                    ),
                }
            )
        return total, data

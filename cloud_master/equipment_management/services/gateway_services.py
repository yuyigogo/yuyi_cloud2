from datetime import datetime
from typing import Optional

from alarm_management.models.alarm_info import AlarmInfo
from cloud.models import bson_to_dict
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
        sensor_id: Optional[str],
        sensor_type: Optional[str],
        is_online: Optional[bool],
    ) -> tuple:
        sensor_query = Q(client_number=client_number)
        if sensor_id:
            sensor_query &= Q(sensor_number=sensor_id)
        if sensor_type:
            sensor_query &= Q(sensor_type=sensor_type)
        if is_online is not None:
            # todo add join index in alarm_info?
            alarm_query = sensor_query & Q(is_online=is_online)
            sensor_ids = AlarmInfo.objects.filter(alarm_query).values_list("sensor_id")
            sensor_query &= Q(sensor_number__in=sensor_ids)
        sensors = SensorConfig.objects.only(
            "sensor_number", "sensor_type", "communication_mode"
        ).filter(sensor_query)
        total = sensors.count()
        sensor_by_page = get_objects_pagination(page, limit, sensors)
        sensor_ids = sensor_by_page.values_list("sensor_number")
        # query sensor_data , not
        data = [
            {
                "name": f"{sensor_type}传感器",
                "sensor_id": sensor_config.sensor_number,
                "sensor_type": sensor_config.sensor_type,
            }
            for sensor_config in sensor_by_page
        ]

        return total, data

    @classmethod
    def _get_sensor_info_in_gateway(cls, sensor_ids: list) -> dict:
        alarm_infos = AlarmInfo.objects.filter(is_latest=True, sensor_id__in=sensor_ids)
        return {alarm_info.sensor_id: {
            "sensor_data_id": str(alarm_info.pk),
            "is_online": alarm_info.is_online,
            "upload_interval": alarm_info.upload_interval,
            "update_time": bson_to_dict(alarm_info.create_date),
        } for alarm_info in alarm_infos}

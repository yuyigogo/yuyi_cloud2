from datetime import datetime

from common.framework.service import BaseService
from equipment_management.models.gateway import GateWay


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
    def get_sensor_info_in_gateway(cls, client_number: str):
        sensor_ids = GateWay.objects.get(client_number=client_number).sensor_ids
        pass

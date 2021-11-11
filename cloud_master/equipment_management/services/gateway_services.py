from datetime import datetime

from common.framework.service import BaseService
from equipment_management.models.gateway import GateWay


class GatewayService(BaseService):
    @classmethod
    def create_gateway(cls, data: dict, site_id: str) -> GateWay:
        gateway = GateWay(
            name=data["name"],
            customer=data["customer"],
            client_number=data["client_number"],
            time_adjusting=datetime.fromtimestamp(data["time_adjusting"]),
            site_id=site_id,
            remarks=data.get("remarks")
        )
        gateway.save()
        return gateway

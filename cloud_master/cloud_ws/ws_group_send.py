import logging

from channels.layers import get_channel_layer
from cloud_ws.sensor_list_consumers import SensorListConsumer

logger = logging.getLogger(__name__)


class WsSensorDataSend(object):
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id

    def ws_send(self, data: dict):
        sensor_id_group_names = SensorListConsumer.ws_sensor_id_to_group_names
        group_names = sensor_id_group_names.get(self.sensor_id)
        if not group_names:
            logger.info(f"[WebSocket send] {self.sensor_id=} not found")
        else:
            channel_layer = get_channel_layer()
            for group_name in group_names:
                try:
                    await channel_layer.group_send(
                        group_name, {"type": "deal_send_sensor_data", "data": data}
                    )
                except Exception as e:
                    logger.warning(
                        f"[WebSocket send err] ignore. {self.sensor_id=} {group_name=} {type(e).__name__}: {e}"
                    )

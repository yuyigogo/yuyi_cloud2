import json
import logging

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from cloud_ws.sensor_list_consumers import SensorListConsumer

logger = logging.getLogger(__name__)


class WsSensorDataSend(object):
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id

    def ws_send(self, data: dict):
        print("2"*100)
        data = {"name": "yuyi"}
        sensor_id_group_names = SensorListConsumer.ws_sensor_id_to_group_names
        group_names = sensor_id_group_names.get(self.sensor_id)
        group_names = ["sensor_list-page_code-3333-sensor_id-584e500400200002"]
        if not group_names:
            logger.info(f"[WebSocket send] {self.sensor_id=} not found")
        else:
            channel_layer = get_channel_layer()
            for group_name in group_names:
                try:
                    # await channel_layer.group_send(
                    #     group_name, {"type": "deal_send_sensor_data", "data": data}
                    # )
                    async_to_sync(channel_layer.group_send)(group_name, {"type": "deal_send_sensor_data", "data": data})
                except Exception as e:
                    logger.warning(
                        f"[WebSocket send err] ignore. {self.sensor_id=} {group_name=} {type(e).__name__}: {e}"
                    )

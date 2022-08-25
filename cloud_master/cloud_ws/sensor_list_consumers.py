import json
import logging
from collections import defaultdict

from channels.generic.websocket import AsyncWebsocketConsumer

from common.const import WebsocketCode
from common.storage.redis import ws_redis

logger = logging.getLogger(__name__)


class SensorListConsumer(AsyncWebsocketConsumer):
    ws_sensor_id_to_group_names = defaultdict(set)

    @classmethod
    def is_valid_page_code(cls, page_code):
        return page_code == WebsocketCode.SENSOR_LIST_PAGE.value

    async def connect(self):
        sensor_data = self.scope["url_route"]["kwargs"]
        page_code = sensor_data["page_code"]
        self.sensor_id = sensor_data["sensor_id"]
        user = self.scope["user"]
        # if not self.is_valid_page_code(page_code):
        #     logger.info(f"invalid page_code: {page_code}")
        #     # reject invali ws, just call close()
        #     await self.close()

        self.sensor_group_name = (
            f"sensor_list-page_code-{page_code}-sensor_id-{self.sensor_id}"
        )
        # Join sensor group
        await self.channel_layer.group_add(self.sensor_group_name, self.channel_name)
        self.ws_sensor_id_to_group_names[self.sensor_id].add(self.sensor_group_name)

        await self.accept()
        logger.info(f"connect ws succeed to {self.sensor_group_name=}")

    async def disconnect(self, close_code):
        # Leave sensor group
        await self.channel_layer.group_discard(
            self.sensor_group_name, self.channel_name
        )
        logger.info(f"disconnect to {self.sensor_group_name=}")
        real_key_name = self.channel_layer._group_key(self.sensor_group_name)
        if not ws_redis.zcard(real_key_name):
            self.ws_sensor_id_to_group_names[self.sensor_id].discard(
                self.sensor_group_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        logger.info(f"received ws data in {self.sensor_group_name=} with {text_data=}")
        # Send message to room group
        await self.channel_layer.group_send(
            self.sensor_group_name, {"type": "deal_send_sensor_data", "data": data}
        )

    # Receive message from sensor group
    async def deal_send_sensor_data(self, event):
        data = event["data"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": data}))

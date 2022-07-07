import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
logger = logging.getLogger(__name__)


class SensorListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        sensor_type_id = self.scope['url_route']['kwargs']
        sensor_type = sensor_type_id["sensor_type"]
        sensor_id = sensor_type_id["sensor_id"]
        self.sensor_group_name = f"sensor_list-sensor_type-{sensor_type}-sensor_id-{sensor_id}"

        # Join sensor group
        await self.channel_layer.group_add(
            self.sensor_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"connect ws succeed to {self.sensor_group_name=}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.sensor_group_name,
            self.channel_name
        )
        logger.info(f"disconnect to {self.sensor_group_name=}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        logger.info(f"received ws data in {self.sensor_group_name=} with {text_data=}")
        # Send message to room group
        await self.channel_layer.group_send(
            self.sensor_group_name,
            {
                'type': 'deal_send_sensor_data',
                'data': data
            }
        )

    # Receive message from room group
    async def deal_send_sensor_data(self, event):
        data = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': data
        }))

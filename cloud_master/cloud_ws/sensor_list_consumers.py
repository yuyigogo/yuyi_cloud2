import json
from channels.generic.websocket import AsyncWebsocketConsumer


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

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.sensor_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.sensor_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

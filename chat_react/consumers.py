import datetime
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = self.room_name.replace(' ', "_")
        self.room_group_name = f'chat_{self.room_name}'


        # join the room
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        utc_time = utc_time.isoformat()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'utc_time': utc_time
            }
        )



    def chat_message(self, event):

        message = event['message']
        utc_time = event['utc_time']
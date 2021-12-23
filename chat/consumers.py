import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import WebsocketConsumer
import datetime

from tickers.models import Ticker


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = self.room_name.replace(' ', '_')
        self.room_group_name = f'chat_{self.room_name}'
        print('i am here', self.room_name) 
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    
    def disconnect(self, code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print('receive', message) 
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
        print('chat message')
        message = event['message']
        utc_time = event['utc_time']
        self.send(text_data=json.dumps({
                'message': 'Loading Data Wait a little...',
                'utc_time': utc_time
            }))
        ticker_qs = Ticker.objects.filter(ticker=message)
        ticker = ticker_qs.first() if ticker_qs.exists() else None
         
        if ticker:
            ticker.update_ticker_data()
            self.send(text_data=json.dumps({
                'message': f'{ticker.title} - {ticker.price}',
                'utc_time': utc_time
            }))
        else:
             self.send(text_data=json.dumps({
                'message': 'No data',
                'utc_time': utc_time
            }))

'''
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))


class EchoConsumer(SyncConsumer):
    channel_layer_alias = "echo_alias"

    def websocket_connect(self, event):
        self.send({
            "type": 'websocket.accept'
        }
        )

    def websocket_receive(self, event):
        self.send({
            "type": 'websocket.send',
            "text": event['text']
        }

        )


class AsyncEchoConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({
            "type": "websoket.accept"
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"]
        })

class MyConsumer(WebsocketConsumer):
    groups = ['broadcast']

    def connect(self):
        self.accept()

'''
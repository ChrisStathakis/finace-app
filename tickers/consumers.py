from channels.generic.websocket import WebsocketConsumer
from  django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from .models import Ticker
from time import sleep
import json
import decimal
import random


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self).default(o)


class TickerConsumer(WebsocketConsumer):

    def connect(self):
        
        self.ticker_name = self.scope['url_route']['kwargs']['ticker_name']
        self.ticker_group_name = f'ticker_{self.ticker_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.ticker_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.ticker_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        async_to_sync(self.channel_layer.group_send)(
            self.ticker_group_name,
            {
                'type': 'ticker_update',
                'message': message
                
            }
        )

    def ticker_update(self, event):
        message = event['message']
        ticker = get_object_or_404(Ticker, ticker=message)
        ticker.update_ticker_data()
        self.send(
            text_data=json.dumps({
                'message': f'{ticker.title} - {ticker.price}',
                'price': f'{ticker.price}',
                
            })
        )
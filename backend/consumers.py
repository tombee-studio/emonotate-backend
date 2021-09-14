from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from users.models import Log


class ExperimentConsumer(AsyncWebsocketConsumer):
    def connect(self, room):
        self.accept()
        print(room)
    
    def disconnect(self, close_code):
        pass
    
    def receive(self, text_data=None, bytes_data=None):
        """
        受け取ったメッセージをそのままオウム返しに戻す
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
    
    @database_sync_to_async
    def _save_log(self, room, description, state, content_id=None, value_type_id=None):
        Log.objects.create(
            content=content_id,
            value_type=value_type_id,
            room=room,
            description=description,
            state=state
        )

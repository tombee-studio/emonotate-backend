from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
import json

from users.models import Log


class ExperimentConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self._save_log(room=self.room_name, 
            description="connected", 
            state='connected')
    
    def disconnect(self, close_code):
        self._save_log(room=self.room_name, 
            description="disconnected", 
            state='disconnected')
        self.close()
    
    def _save_log(self, room, description, state, content_id=None, value_type_id=None):
        Log.objects.create(
            content=content_id,
            value_type=value_type_id,
            room=room,
            description=description,
            state=state
        )

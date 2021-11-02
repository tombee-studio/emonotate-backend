from channels.generic.websocket import WebsocketConsumer


class ExperimentConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.room_name = self.scope['url_route']['kwargs']['room_name']

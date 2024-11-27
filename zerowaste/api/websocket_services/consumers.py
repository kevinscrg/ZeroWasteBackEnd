import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        # Acceptăm conexiunea, dar nu adăugăm încă canalul la grup
        self.accept()
        self.send(text_data=json.dumps({
            'message': 'Conectat la WebSocket. Aștept autorizarea.',
            'type': 'connected',
        }))

    def disconnect(self, close_code):
        # Scoate canalul din grup la deconectare
        async_to_sync(self.channel_layer.group_discard)(
            "notifications",
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'authorization':
            # Procesăm autorizarea
            token = data['payload'].get('token')
            share_code = data['payload'].get('share_code')
            if token:
                async_to_sync(self.channel_layer.group_add)(
                    f"notifications{share_code}",
                    self.channel_name
                )

                self.send(text_data=json.dumps({
                    'type': 'authorization',
                    'payload': {
                        'message': 'Autorizat cu succes',
                        'status': 'success'
                    }
                }))
               
            else:
                self.close()
        else:
            async_to_sync(self.channel_layer.group_send)(
                "notifications",
                {
                    "type": "chat_message",
                    "message": data['payload']
                }
            )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'message',
            'payload': message
        }))


class PythonScriptConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            "python_scripts",
            self.channel_name
        )
        self.send(text_data=json.dumps({
            'message': 'Conectat la WebSocket',
            'type': 'connected',
        }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "python_scripts", 
            self.channel_name
        )


    def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'run':
            print('Received')
            print(data['payload'])

    def askScript(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'message',
            'payload': message
        }))

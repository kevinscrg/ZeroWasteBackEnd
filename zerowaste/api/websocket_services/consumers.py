import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.core.cache import cache

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.groups_joined = []
        self.accept()
        self.send(text_data=json.dumps({
            'message': 'Conectat la WebSocket. Aștept autorizarea.',
            'type': 'connected',
        }))

    def disconnect(self, close_code):
        for group in self.groups_joined:
            async_to_sync(self.channel_layer.group_discard)(
                group,
                self.channel_name
            )

    def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'authorization':

            token = data['payload'].get('token')
            share_code = data['payload'].get('share_code')
            email = data['payload'].get('email')
            if token:
                group_name_share_code = f"notifications{share_code}"
                group_name_email = f"notifications{email.split('@')[0] + email.split('@')[1]}"

                async_to_sync(self.channel_layer.group_add)(
                    group_name_share_code,
                    self.channel_name
                )
                async_to_sync(self.channel_layer.group_add)(
                    group_name_email,
                    self.channel_name
                )

                self.groups_joined.extend([group_name_share_code, group_name_email])

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
            share_code = data['payload'].get('share_code')
            if not share_code:
                self.send(text_data=json.dumps({
                'type': 'error',
                'payload': {
                    'message': 'Share code is required to send a message.'
                }
            }))
                return
            async_to_sync(self.channel_layer.group_send)(
                f"notifications{share_code}",
                {
                    "type": "productmessage",
                    "message": data['payload']
                }
            )

    def recipe(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'recipe',
            'payload': message
        }))
        
    def productmessage(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'productmessage',
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
            payload = data['payload']
            email = payload.get('email')
            recepies_ids = payload.get('recipe_ids')
            if cache.get(f"recepies_{email}"):
                cache.delete(f"recepies_{email}")
            cache.set(f"recepies_{email}", recepies_ids, timeout=3600)
            
            message = {
                'type': 'recipe',
                'message': 'ok'
            }
            async_to_sync(self.channel_layer.group_send)(
                f"notifications{email.split('@')[0] + email.split('@')[1]}",
                message
            )
            

    def askScript(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'message',
            'payload': message
        }))

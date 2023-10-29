import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from users.models import Chat, Message
from .serializers import *

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.room_name}"

        # Check if the user is allowed to access this chat
        chat = await self.get_chat()
        if not chat:
            await self.close()
            return

        if not await self.user_can_access_chat(chat):
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'load_history':
            chat = await self.get_chat()
            await self.load_chat_history(chat)

        if data['type'] == 'chat_message':
            message_text = data['message']

            user = self.scope['user']
            chat = await self.get_chat()

            try:
                message = await self.create_message(chat, user, message_text)

                serialized_message = await self.serialize_message(message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': serialized_message,
                        'username': user.username,
                        'user_id': user.id
                    }
                )

            except Message.DoesNotExist:
                pass
        
        elif data['type'] == 'message_liked':
            user = self.scope['user']
            chat = await self.get_chat()
        
            try:
                message = await self.get_message(chat, message_id=data['message_id'])
                message = await self.like_or_unlike_message(message, user)
                serialized_message = await self.serialize_message(message)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_liked',
                        'message': serialized_message,
                        'message_id': data['message_id'],
                        'username': user.username,
                        'user_id': user.id
                    }
                )
            except Message.DoesNotExist:
                pass

        elif data['type'] == 'message_deleted':
            user = self.scope['user']
            message_id = data['message_id']

            try:
                message = await self.get_message_by_id(message_id)
                await self.delete_message_by_id(user, message_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_deleted',
                        'message_id': message_id,
                        'username': user.username,
                        'user_id': user.id
                    }
                )
            except Message.DoesNotExist:
                pass

    @sync_to_async
    def serialize_message(self, message):
        serializer = MessageSerializer(message)
        return serializer.data
    
    @sync_to_async
    def serialize_messages(self, messages):
        serializer = MessageSerializer(messages, many=True)
        return serializer.data

    async def load_chat_history(self, chat):
        messages = await self.get_chat_history(chat)
        serialized_messages = await self.serialize_messages(messages)

        await self.send(text_data=json.dumps({
            'type': 'load_history',
            'chat_history': serialized_messages,
        }))
    
    # async def like_message(self, event):
    #     message_id = event['message_id']
    #     user = self.scope['user']
    #     try:
    #         message = await self.get_message_by_id(message_id)

    #         # Check if the user hasn't already liked the message
    #         if user not in message.likes.all():
    #             message.likes.add(user)

    #             # Serialize the liked message
    #             serialized_liked_message = await self.serialize_message(message)

    #             await self.channel_layer.group_send(
    #                 self.room_group_name,
    #                 {
    #                     'type': 'message_liked',
    #                     'message': serialized_liked_message,
    #                     'user_id': user.id
    #                 }
    #             )
    #     except Message.DoesNotExist:
    #         pass

    # async def delete_message(self, event):
    #     message_id = event['message_id']
    #     user = self.scope['user']
    #     try:
    #         await self.delete_message_by_id(user, message_id)

    #         await self.channel_layer.group_send(
    #             self.room_group_name,
    #             event
    #         )
    #     except Message.DoesNotExist:
    #         pass

    @database_sync_to_async
    def delete_message_by_id(self, user, message_id):
        message = Message.objects.filter(id=message_id).first()
        if user == message.sender:
            message.delete()

    @database_sync_to_async
    def get_message_by_id(self, message_id):
        return Message.objects.get(id=message_id)
    
    @database_sync_to_async
    def get_chat_history(self, chat):
        return Message.objects.filter(chat=chat).order_by('created_at')

    @database_sync_to_async
    def create_message(self, chat, sender, message_text):
        return Message.objects.create(chat=chat, sender=sender, text=message_text)

    @database_sync_to_async
    def get_message(self, chat, message_id):
        return Message.objects.get(chat=chat, id=message_id)
    
    @database_sync_to_async
    def get_chat(self):
        return Chat.objects.get(id=int(self.room_name))

    @database_sync_to_async
    def like_or_unlike_message(self, message, user):
        if user not in message.likes.all():
            message.likes.add(user)
        else:
            message.likes.remove(user)
        return message
    
    @database_sync_to_async
    def user_can_access_chat(self, chat):
        return self.scope['user'] in chat.users.all()
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id']
        }))

    async def message_liked(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_liked',
            'message': event['message'],
            'message_id': event['message_id'],
            'username': event['username'],
            'user_id': event['user_id']
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'username': event['username'],
            'user_id': event['user_id']
        }))
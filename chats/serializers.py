import base64
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import CustomUser
from django.core.cache import cache
import datetime
from django.utils import timezone
from django.conf import Settings
from users.models import Chat, ChatUser, Message, Folder
from users.serializers import ShortUserSerializer, UserSerializer
from users.utils import check_blocked

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'sender_username', 'text', 'created_at', 'likes', 'chat')

    # def to_representation(self, instance):
    #     return super().to_representation(instance)

# class CreateMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = ('sender', 'text', 'chat')

#     def validate(self, data):
#         sender = self.context['request'].user
#         chat_id = data['chat']

#         try:
#             chat = Chat.objects.get(id=chat_id)
#         except Chat.DoesNotExist:
#             raise serializers.ValidationError("Chat with the provided ID does not exist.")

#         if len(chat.chat_users.all()) == 2:
#             users = chat.chat_users.exclude(user=sender)
#             recepient = users.first().user
#             if not check_blocked(user=recepient, requested_by_user=sender):
#                 raise serializers.ValidationError("You are blocked from sending messages to this user.")
#         return data


class ChatUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()  

    class Meta:
        model = ChatUser
        fields = ('id', 'user', 'chat', 'role')


class ShortChatSerializer(serializers.ModelSerializer):
    last_message = MessageSerializer(source='get_last_message', read_only=True)
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        return ShortUserSerializer(obj.users.all(), 
            many=True, read_only=True, context={'request': self.context['request']}).data

    class Meta:
        model = Chat
        fields = ('id', 'users', 'last_message')

class ChatSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    def get_messages(self, obj):
        messages = obj.chat_messages.all()
        return MessageSerializer(messages, many=True).data

    class Meta:
        model = Chat
        fields = '__all__'

class FolderSerializer(serializers.ModelSerializer):
    chat_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ('id', 'name', 'chat_count')

    def get_chat_count(self, obj):
        return obj.chats.count()
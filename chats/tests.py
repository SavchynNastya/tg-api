
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser as User, Chat, ChatUser, Folder
from rest_framework.authtoken.models import Token


class ChatsFoldersTestCases(APITestCase):
    def setUp(self):
        self.root_url = 'http://localhost:9000/api'
        self.user1 = User.objects.create_user(username='test_user1', password='password1', phone_number='+380926386428')
        self.user2 = User.objects.create_user(username='test_user2', password='password2', phone_number='+380926386429')
        self.user3 = User.objects.create_user(username='test_user3', password='password3', phone_number='+380926386430')
        self.user4 = User.objects.create_user(username='test_user4', password='password4', phone_number='+380926386431')
        self.user = User.objects.create_user(
            username='test_user',
            phone_number='+380926386482', 
            password='kpi2023_test'
        )
        self.test_chat = Chat.objects.create_chat(creator=self.user3, name='Chat_test_3', user_ids=[self.user2.id,])
        self.test_chat1 = Chat.objects.create_chat(creator=self.user, name='Chat_test_1', user_ids=[self.user3.id,])
        self.test_chat2 = Chat.objects.create_chat(creator=self.user4, name='Chat_test_4', user_ids=[self.user1.id,])
        self.test_folder = Folder.objects.create_folder(owner=self.user4, 
            name='Test_folder', 
            chat_ids=[self.test_chat2.id,]
        )
        self.user.is_active = True
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_create_chat(self):
        url = f'{self.root_url}/chats/'
        data = {'user_ids': [self.user1.id, self.user2.id]} 
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_chat(self):
        url = f'{self.root_url}/chats/{self.test_chat.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_chats(self):
        url = f'{self.root_url}/chats/list/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        for obj in response.data:
            for field in ('id', 'users', 'last_message'):
                self.assertIn(field, obj, f"Field '{field}' is missing in the serialized data")
            self.assertIsInstance(obj, dict)
            for user in obj['users']:
                for field in ('id', 'username', 'profile_pic', 'online'):
                    self.assertIn(field, user, f"Field '{field}' is missing in the serialized data")
     
    def test_add_user_to_chat(self):
        url = f'{self.root_url}/chats/{self.test_chat1.id}/add-user/{self.user2.id}/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user2.id, [user.id for user in self.test_chat1.users.all()])

    def test_delete_user_from_chat(self):
        url = f'{self.root_url}/chats/{self.test_chat1.id}/delete-user/{self.user3.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.user3.id, [user.id for user in self.test_chat1.users.all()])

    def test_grant_role_to_user(self):
        url = f'{self.root_url}/chats/{self.test_chat1.id}/role/{self.user3.id}/'
        data = {'new_role': 'editor'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chat_user = ChatUser.objects.get(chat=self.test_chat1, user=self.user3)
        self.assertEqual(chat_user.role, 'editor')

    def test_get_chat_user(self):
        url = f'{self.root_url}/chats/{self.test_chat.id}/user/{self.user2.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ('id', 'user', 'chat', 'role'):
            self.assertIn(field, response.data, f"Field '{field}' is missing in the serialized data")

    def test_create_folder(self):
        url = f'{self.root_url}/folder/'
        data = {'name': 'Test Folder', 'chat_ids': [self.test_chat.id,]}  
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in ('id', 'name', 'chat_count'):
            self.assertIn(field, response.data, f"Field '{field}' is missing in the serialized data")

    def test_rename_folder(self):
        url = f'{self.root_url}/folder/{self.test_folder.id}/rename/'
        data = {'new_name': 'Renamed Folder'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_folder_chats(self):
        url = f'{self.root_url}/folder/{self.test_folder.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        for obj in response.data:
            for field in ('id', 'users', 'last_message'):
                self.assertIn(field, obj, f"Field '{field}' is missing in the serialized data")
            self.assertIsInstance(obj, dict)
            for user in obj['users']:
                for field in ('id', 'username', 'profile_pic', 'online'):
                    self.assertIn(field, user, f"Field '{field}' is missing in the serialized data")

    def test_folder_list(self):
        url = f'{self.root_url}/folder/list/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for obj in response.data:
            for field in ('id', 'name', 'chat_count'):
                self.assertIn(field, obj, f"Field '{field}' is missing in the serialized data")

    def test_add_to_folder(self):
        url = f'{self.root_url}/folder/{self.test_folder.id}/add/{self.test_chat.id}/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
   
    def test_remove_from_folder(self):
        url = f'{self.root_url}/folder/{self.test_folder.id}/remove/{self.test_chat.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_folder(self):
        url = f'{self.root_url}/folder/{self.test_folder.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TestCase
from unittest.mock import MagicMock
from .consumers import ChatConsumer
import json


class ChatConsumerTestCase(TestCase):
    def setUp(self):
        # Set up test data, mock objects, etc.
        pass

    def test_connect(self):
        communicator = WebsocketCommunicator(ChatConsumer, "/ws/chat/1/")
        connected, _ = communicator.connect()
        self.assertTrue(connected)
        # Add assertions for connect method
        
    def test_disconnect(self):
        communicator = WebsocketCommunicator(ChatConsumer, "/ws/chat/1/")
        connected, _ = communicator.connect()
        self.assertTrue(connected)
        disconnected = communicator.disconnect()
        self.assertTrue(disconnected)
        # Add assertions for disconnect method

    def test_receive_load_history(self):
        communicator = WebsocketCommunicator(ChatConsumer, "/ws/chat/1/")
        connected, _ = communicator.connect()
        self.assertTrue(connected)
        communicator.send_json_to({
            "type": "load_history",
            # Add necessary data
        })
        response = communicator.receive_json_from()
        # Add assertions for receive method with 'load_history' type
        
    def test_receive_chat_message(self):
        communicator = WebsocketCommunicator(ChatConsumer, "/ws/chat/1/")
        connected, _ = communicator.connect()
        self.assertTrue(connected)
        communicator.send_json_to({
            "type": "chat_message",
            # Add necessary data
        })
        response = communicator.receive_json_from()
        # Add assertions for receive method with 'chat_message' type

    def test_receive_message_liked(self):
        communicator = WebsocketCommunicator(ChatConsumer, "/ws/chat/1/")
        connected, _ = communicator.connect()
        self.assertTrue(connected)
        communicator.send_json_to({
            "type": "message_liked",
            # Add necessary data
        })
        response = communicator.receive_json_from()
        # Add assertions for receive method with 'message_liked' type

    def test_receive_message_deleted(self):
        communicator = WebsocketCommunicator(ChatConsumer, "/ws/chat/1/")
        connected, _ = communicator.connect()
        self.assertTrue(connected)
        communicator.send_json_to({
            "type": "message_deleted",
            # Add necessary data
        })
        response = communicator.receive_json_from()
        # Add assertions for receive method with 'message_deleted' type

    # Additional test methods for other functionalities

    def tearDown(self):
        # Clean up resources, if any
        pass

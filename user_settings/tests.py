
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser as User
from django.urls import reverse
from rest_framework.authtoken.models import Token


class UserSettingsTestCases(APITestCase):
    def setUp(self):
        self.root_url = 'http://localhost:9000/api'
        self.user_to_block = User.objects.create_user(
            username='test_block_user',
            phone_number='+380926386400', 
            password='kpi2023_test1'
        )
        self.user = User.objects.create_user(
            username='test_user',
            phone_number='+380926386482', 
            password='kpi2023_test'
        )
        self.user.is_active = True
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_get_user_settings(self):
        url = f'{self.root_url}/settings/'
        response = self.client.get(url)
        print('<---- GET SETTINGS test ---->')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('blocked_users' in response.data)
        self.assertTrue('hide_phone_number' in response.data)
        self.assertTrue('hide_photo' in response.data)
        self.assertTrue('hide_online' in response.data)

    def test_update_user_settings(self):
        url = f'{self.root_url}/settings/'
        data = {
            "hide_phone_number": True,  
            "hide_photo": False,
            "hide_online": True
        }
        response = self.client.patch(url, data, format='json')
        print('<---- UPDATE SETTINGS test ---->')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['hide_phone_number'], data['hide_phone_number'])
        self.assertEqual(response.data['hide_photo'], data['hide_photo'])
        self.assertEqual(response.data['hide_online'], data['hide_online'])

    def test_block_unblock_user(self):
        url = f'{self.root_url}/settings/block-user/{self.user_to_block.id}/'
        response = self.client.post(url, {'id': self.user_to_block.id}, format='json')
        print('<---- BLOCK USER test ---->')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_to_block.id, [user.id for user in self.user.user_settings.blocked_users.all()])
        url = f'{self.root_url}/settings/unblock-user/{self.user_to_block.id}/'
        response = self.client.post(url, {'id': self.user_to_block.id}, format='json')
        print('<---- UNBLOCK USER test ---->')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_to_block.id, [user.id for user in self.user.user_settings.blocked_users.all()])

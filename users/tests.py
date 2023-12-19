# from django.test import TestCase
# from rest_framework.test import APIRequestFactory
# from rest_framework.test import force_authenticate
# from users.models import CustomUser
# from users.views import get_user


# factory = APIRequestFactory()
# user = CustomUser.objects.get(username='test_user')
# view = get_user()

# request = factory.get('/users/self/')
# force_authenticate(request, user=user)
# response = view(request)

import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser as User
from django.urls import reverse
from rest_framework.authtoken.models import Token

class UserTestCases(APITestCase):
    def setUp(self):
        self.root_url = 'http://localhost:9000/api'
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

    def test_generate_otp(self):
        url = f'{self.root_url}/auth/generate_otp/'
        data = {'phone_number': '+380926386488'} 
        response = self.client.post(url, data,  format='json')
        print('<---- GENERATE OTP test ---->')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_username_and_status(self):
        url = f'{self.root_url}/users/update-username-status/'
        data = {
            'username': 'newusername',
            'status': 'active'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print('<---- UPDATE PROFILE DATA test ---->')
        print(response.data)
        self.assertEqual(response.data['status'], 'active')

    def test_get_user(self):
        url = f'{self.root_url}/users/self/'
        response = self.client.get(url)
        print('<---- GET USER DATA test ---->')
        for field in ('id', 'username', 'profile_pic', 'status', 'phone_number', 'last_seen', 'online'):
            self.assertIn(field, response.data, f"Field '{field}' is missing in the serialized data")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users(self):
        url = f'{self.root_url}/users/' 
        response = self.client.get(url)
        print('<---- GET USERS DATA test ---->')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

        for field in ('total_objects', 'objects_per_page', 'current_page'):
            self.assertIn(field, response.data, f"Field '{field}' is missing in the serialized pagination data")
        
        for item in response.data['results']:
            self.assertIsInstance(item, dict)
            for field in ('id', 'username', 'profile_pic', 'status', 'phone_number', 'last_seen', 'online'):
                self.assertIn(field, item, f"Field '{field}' is missing in the serialized data")

    def test_update_profile_pic_endpoint(self):
        url = f'{self.root_url}/users/profile-pic/' 
        test_image_path = f'{os.getcwd()}\\users\\test_files\\image.jpg'
        with open(test_image_path, 'rb') as f:
            image_file = {'image': f}
            response = self.client.patch(url, data=image_file, format='multipart')
            print('<---- UPDATE USER PICTURE test ---->')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        User.objects.create_user(
            username='test_login_user',
            phone_number='+380926386480', 
            password='kpi2023_test1'
        )
        url = f'{self.root_url}/auth/generate_otp/'
        data = {'phone_number': '+380926386480'} 
        response = self.client.post(url, data,  format='json')
        url = f'{self.root_url}/auth/login/'
        data = {'phone_number': '+380926386480', 'otp': '0000'} 
        response = self.client.post(url, data,  format='json')
        print('<---- LOGIN test ---->')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data, msg='Token is missing.')

    def test_logout(self):
        url = f'{self.root_url}/auth/logout/'
        response = self.client.post(url)
        print('<---- LOGOUT test ---->')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# from rest_framework.test import RequestsClient
# from rest_framework.test import APITestCase


# class TestUserAPI(APITestCase):
#     client = RequestsClient()
#     token = '6d0fb8ba876cb2b209fb12e0686707ed67a4c01c'

#     def test_update_username_and_status(self):
#         response = self.client.patch(
#         'http://localhost:9000/api/users/update-username-status/', 
#         json={'status': 'status_upd'},
#         headers={'Authorization': f'Token {self.token}'})
#         print(response)
#         assert response.status_code == 200
#         assert response.data['status'] == 'status_upd'

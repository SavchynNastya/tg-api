from rest_framework import status, mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
import phonenumbers
import datetime
from .models import CustomUser as User


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_otp(request):
    phone_number = request.data.get('phone_number')
    if phone_number:
        phone_number = phonenumbers.parse(phone_number, None)
        if phonenumbers.is_valid_number(phone_number):
            otp = '0000'
            user, created = User.objects.get_or_create(
                phone_number=phonenumbers.format_number(
                    phone_number, phonenumbers.PhoneNumberFormat.E164
                ),
            )
            if created:
                user.username=f"user" + get_random_string(3, '0987654321')
            user.otp_secret=otp
            user.save()
            return Response(status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Phone Number'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    user = request.user
    user.auth_token.delete()
    user.save()
    return Response('OK', status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    queryset = User.objects.all()
    # serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'message': 'Wrong otp.'}, status=status.HTTP_201_CREATED)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_username_and_status(request):
    serializer = UserUpdateSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        username = serializer.validated_data.get('username')
        user_status = serializer.validated_data.get('status')
        if username:
            user.username = username
        if user_status:
            user.status = user_status
        user.save()
        return Response('OK', status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, id):
    if id == 'self':
        serializer = UserSerializer(request.user, context={'self': True, 'request': request})
    else:
        user = get_object_or_404(User, pk=id)
        if not user:
            return Response({'error': 'User was not found.'}, status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user, context={'self': False, 'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    query = request.query_params.get('query', None)
    page = int(request.query_params.get('page', 1))
    page_size = 8

    users = User.objects.all()
    if query:
        users = users.filter(username__icontains=query)
    total_objects = users.count()

    end = page * page_size
    items = list(users[:end])
    serializer = UserSerializer(items, many=True, context={'self': False, 'request': request})
    response_data = {
        'total_objects': total_objects,
        'objects_per_page': page_size,
        'current_page': page,
        'results': serializer.data,
    }
    if page > 1:
        response_data['previous_page'] = page - 1

    if end < total_objects:
        response_data['next_page'] = page + 1

    return Response(response_data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_pic(request):
    try:
        serializer = ProfilePictureUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data.get('phone_number')
        otp = serializer.validated_data.get('otp')

        phone_number = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_valid_number(phone_number):
            return Response({'error': 'Invalid Phone Number'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone_number=phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)).first()
        if user and user.otp_secret == otp:
            token, created = Token.objects.get_or_create(user=user)
            first_login = True if user.last_login is None else False
            user.last_login = datetime.datetime.now()
            user.save()
            return Response({'token': token.key, 'first_login': first_login}, status=status.HTTP_200_OK)
        elif not user:
            return Response({'error': 'User is not registered'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from users.serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from users.models import UserSettings, CustomUser as User


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    user = request.user
    if request.method == 'GET':
        try:
            settings = UserSettings.objects.get(user=user)
            serializer = UserSettingsSerializer(settings, context={'request': request})
            return Response(serializer.data)
        except UserSettings.DoesNotExist:
            return Response({'message': 'User settings not found.'}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PATCH':
        try:
            settings = UserSettings.objects.get(user=user)
            serializer = UpdateUserSettingsSerializer(settings, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except UserSettings.DoesNotExist:
            return Response({'message': 'User settings not found.'}, status=status.HTTP_404_NOT_FOUND)
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request, id):
    user_settings = request.user.user_settings
    blocked_users = user_settings.blocked_users
    user = get_object_or_404(User, pk=id)
    blocked_users.add(user)
    serializer = UserSerializer(blocked_users.all(), many=True, context={'self': False, 'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unblock_user(request, id):
    user_settings = request.user.user_settings
    blocked_users = user_settings.blocked_users
    user = get_object_or_404(User, pk=id)
    blocked_users.remove(user)
    serializer = UserSerializer(blocked_users.all(), many=True, context={'self': False, 'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
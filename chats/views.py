from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from users.serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from users.models import UserSettings, CustomUser as User, Message, Chat, ChatUser, Folder
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from users.utils import check_blocked


"""
CHATS
"""

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_chats(request):
    chats = request.user.chats.all()
    serializer = ShortChatSerializer(chats, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat(request):
    user_ids = request.data['user_ids']
    chat = Chat.objects.create_chat(creator=request.user, name=None, user_ids=user_ids)
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat(request, id):
    chat = get_object_or_404(Chat, pk=id)
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user(request, id, user_id):
    chat = get_object_or_404(Chat, pk=id)
    Chat.objects.add_user(by_user=request.user, chat_id=id, user_id=user_id, role=None)
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, id, user_id):
    chat = get_object_or_404(Chat, pk=id)
    Chat.objects.remove_user(by_user=request.user, chat_id=id, user_id=user_id)
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def grant_role(request, id, user_id):
    chat = get_object_or_404(Chat, pk=id)
    Chat.objects.change_user_role(by_user=request.user, chat_id=id, user_id=user_id, new_role=request.data['new_role'])
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_user(request, id, user_id):
    chat = get_object_or_404(Chat, pk=id)
    user = get_object_or_404(CustomUser, pk=user_id)
    chat_user = get_object_or_404(ChatUser, chat=chat, user=user)
    serializer = ChatUserSerializer(chat_user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chats_by_user_id(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    chats = Chat.objects.filter(users=user)
    serializer = ChatSerializer(chats, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)



"""
MESSAGES
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    if not 'chat_id' or not 'text' in request.data:
        return Response({'error': 'chat_id and text should be passed.'}, status=status.HTTP_400_BAD_REQUEST)
    message = Message.objects.create_message(sender=request.user, 
                                             text=request.data['text'], 
                                             chat_id=request.data['chat_id'])
    
    serialized_message = MessageSerializer(message)
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     f"chat_{message.chat.id}",
    #     {
    #         "type": "chat_message",
    #         "message": serialized_message.data,
    #     },
    # )

    return Response(serialized_message.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_message(request, id):
    message = get_object_or_404(Message, id=id)
    message.likes.add(request.user)
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     f"chat_{message.chat.id}",
    #     {
    #         "type": "message_liked",
    #         "message": serialized_message.data,
    #     },
    # )

    return Response(len(message.likes.all()), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_message(request, id):
    message = get_object_or_404(Message, id=id)
    message.delete()
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     f"chat_{message.chat.id}",
    #     {
    #         "type": "message_deleted",
    #         "message": serialized_message.data,
    #     },
    # )

    return Response(status=status.HTTP_204_NO_CONTENT)


"""
CHAT FOLDERS
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_folder(request):
    if not 'chat_ids' or not 'name' in request.data:
        return Response('chat_ids and folder name should be passed', 
                        status=status.HTTP_400_BAD_REQUEST)
    
    folder = Folder.objects.create_folder(owner=request.user, 
                                 name=request.data['name'], 
                                 chat_ids=request.data['chat_ids'])
    serializer = FolderSerializer(folder, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_folder(request, id):
    Folder.objects.delete_folder(folder_id=id)
    return Response('OK', status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rename_folder(request, id):
    if not 'new_name' in request.data:
        return Response('new_name should be passed to rename the folder', 
                        status=status.HTTP_400_BAD_REQUEST)
    Folder.objects.rename_folder(folder_id=id, new_name=request.data['new_name'])
    return Response('OK', status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_folder_chats(request, id):
    folder_chats = Folder.objects.get_chats_in_folder(folder_id=id)
    serializer = ShortChatSerializer(folder_chats, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def folder_list(request):
    folder_chats = Folder.objects.folder_list(owner=request.user)
    serializer = FolderSerializer(folder_chats, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_folder(request, id, chat_id):
    Folder.objects.add_chat_to_folder(folder_id=id, chat_id=chat_id)
    return Response('OK', status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_folder(request, id, chat_id):
    Folder.objects.remove_chat_from_folder(folder_id=id, chat_id=chat_id)
    return Response('OK', status=status.HTTP_204_NO_CONTENT)

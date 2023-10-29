from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from users.utils import check_blocked
from rest_framework.generics import get_object_or_404


class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone_number, password=None):
        if not username:
            raise ValueError('The Username field must be set')
        if not phone_number:
            raise ValueError('The Phone Number field must be set')

        user = self.model(
            username=username,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=40, unique=True)
    profile_pic = models.ImageField(upload_to='pictures/profile/', blank=True, null=True)
    status = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    otp_secret = models.CharField(max_length=29)
    last_seen = models.DateTimeField(null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',
    )

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.pk:
            super(CustomUser, self).save(*args, **kwargs)
            UserSettings.objects.create(user=self)
        else:
            user = CustomUser.objects.get(pk=self.pk)
            self.pk = user.pk
            super(CustomUser, self).save(*args, **kwargs)
    
class ChatManager(models.Manager):
    def create_chat(self, creator, name=None, user_ids=[]):
        # Sort the user IDs to ensure consistent chat creation
        user_ids.sort()

        # Check if a chat with the same users already exists
        existing_chat = self.get_existing_chat(user_ids)
        if existing_chat:
            return existing_chat

        chat = self.create(name=name)
        chat.users.add(creator)
        ChatUser.objects.create(user=creator, chat=chat, role='owner')
        for user_id in user_ids:
            user = CustomUser.objects.get(pk=user_id)
            ChatUser.objects.create(user=user, chat=chat)
            chat.users.add(user)
        return chat

    def get_existing_chat(self, user_ids):
        # Sort the user IDs to ensure consistent comparison
        user_ids.sort()

        # Find chats that have the exact same set of users
        chats = Chat.objects.filter(users__in=user_ids)
        for chat in chats:
            chat_user_ids = chat.users.values_list('id', flat=True)
            chat_user_ids = list(chat_user_ids)
            chat_user_ids.sort()
            if user_ids == chat_user_ids:
                return chat
        return None
    
    def add_user(self, by_user, chat_id, user_id, role=None):
        chat = get_object_or_404(Chat, pk=chat_id)
        by_user_chat_user = get_object_or_404(ChatUser, user=by_user, chat=chat)
        if by_user_chat_user.role in ('editor', 'owner'):
            user = CustomUser.objects.get(pk=user_id)
            chat.users.add(user)
            ChatUser.objects.create(user=user, chat=chat, role=role)

    def remove_user(self, by_user, chat_id, user_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        by_user_chat_user = get_object_or_404(ChatUser, user=by_user, chat=chat)
        if by_user_chat_user.role in ('editor', 'owner'):
            user = CustomUser.objects.get(pk=user_id)
            chat.users.remove(user)
            chat_user = ChatUser.objects.get(chat=chat, user=user)
            chat_user.delete()

    def change_user_role(self, by_user, chat_id, user_id, new_role):
        chat = get_object_or_404(Chat, pk=chat_id)
        by_user_chat_user = get_object_or_404(ChatUser, user=by_user, chat=chat)
        if by_user_chat_user.role == 'owner':
            user = CustomUser.objects.get(pk=user_id)
            chat_user = ChatUser.objects.get(chat=chat, user=user)
            chat_user.role=new_role
            chat_user.save()

class Chat(models.Model):
    users = models.ManyToManyField(CustomUser, related_name='chats')
    name = models.CharField(null=True, max_length=50)
    chat_pic = models.ImageField(upload_to='pictures/chat/', blank=True, null=True)

    objects = ChatManager()

    def get_last_message(self):
        last_message = self.chat_messages.order_by('created_at').last()
        return last_message
    
class FolderManager(models.Manager):
    def get_chats_in_folder(self, folder_id):
        try:
            folder = self.get(pk=folder_id)
            return folder.chats.all()
        except Folder.DoesNotExist:
            return None

    def create_folder(self, owner, name, chat_ids):
        chats = []
        for chat_id in chat_ids:
            chats.append(get_object_or_404(Chat, pk=chat_id))
        folder = self.create(owner=owner, name=name)
        folder.chats.set(chats)
        return folder

    def add_chat_to_folder(self, folder_id, chat_id):
        try:
            folder = self.get(pk=folder_id)
            chat = Chat.objects.get(pk=chat_id)
            folder.chats.add(chat)
        except (Folder.DoesNotExist, Chat.DoesNotExist):
            pass

    def folder_list(self, owner):
        try:
            folders = self.filter(owner=owner)
            return folders
        except (Folder.DoesNotExist, Chat.DoesNotExist):
            pass

    def rename_folder(self, folder_id, new_name):
        try:
            folder = self.get(pk=folder_id)
            folder.name = new_name
            folder.save()
        except Folder.DoesNotExist:
            pass

    def remove_chat_from_folder(self, folder_id, chat_id):
        try:
            folder = self.get(pk=folder_id)
            chat = Chat.objects.get(pk=chat_id)
            folder.chats.remove(chat)
        except (Folder.DoesNotExist, Chat.DoesNotExist):
            pass

    def delete_folder(self, folder_id):
        try:
            folder = self.get(pk=folder_id)
            folder.delete()
        except Folder.DoesNotExist:
            pass

class Folder(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    chats = models.ManyToManyField(Chat, null=True, related_name='folder')

    objects = FolderManager()
    
class ChatUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_users')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)
    role = models.CharField(choices=[('owner', 'owner'), ('editor', 'editor'), (None, None)], max_length=10, null=True)

class MessageManager(models.Manager):
    def create_message(self, sender, text, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            raise Chat.DoesNotExist("Chat with the provided ID does not exist.")
        
        if chat.users.count() == 2:
            for user in chat.users.all():
                if user != sender:
                    recepient = user
            
            if check_blocked(user=recepient, requested_by_user=sender):
                return False
        message = self.create(sender=sender, text=text, chat=chat)
        return message

class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_messages')
    likes = models.ManyToManyField(CustomUser, null=True)

    objects = MessageManager()


class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_settings')
    hide_phone_number = models.BooleanField(default=False)
    hide_photo = models.BooleanField(default=False)
    hide_online = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField(CustomUser, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            super(UserSettings, self).save(*args, **kwargs)
        else:
            existing_settings = UserSettings.objects.get(user=self.user)
            self.pk = existing_settings.pk
            super(UserSettings, self).save(*args, **kwargs)
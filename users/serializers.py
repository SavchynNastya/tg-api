import base64
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import CustomUser
from django.core.cache import cache
import datetime
from django.utils import timezone
from django.conf import settings
from .utils import *

class ShortUserSerializer(serializers.ModelSerializer):
    online = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'profile_pic', 'online')

    def get_online(self, obj):
        if obj.last_seen and not check_blocked(user=obj, \
                requested_by_user=self.context['request'].user):
            now = timezone.now()
            delta = datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
            if now > obj.last_seen + delta:
                return False
            else:
                return True
        else:
            return False

class UserSerializer(serializers.ModelSerializer):
    online = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'profile_pic', 'status', 'phone_number', 'last_seen', 'online')
    
    # def get_profile_pic(self, obj):
    #     if obj.profile_pic:
    #         with obj.profile_pic.open('rb') as image:
    #             image_data = image.read()
    #             base64_encoded_image = base64.b64encode(image_data).decode('utf-8')
    #         return base64_encoded_image
    #     return None

    def get_online(self, obj):
        if obj.last_seen and not check_blocked(user=obj, \
                requested_by_user=self.context['request'].user):
            now = timezone.now()
            delta = datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
            if now > obj.last_seen + delta:
                return False
            else:
                return True
        else:
            return False
        
    def get_last_seen(self, obj):
        return obj.last_seen if not check_blocked(user=obj, \
                requested_by_user=self.context['request'].user) else None
        
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        if 'self' in self.context and not self.context['self'] and obj != self.context['request'].user:
            if not check_blocked(user=obj, requested_by_user=self.context['request'].user):
                representation['phone_number'] = obj.phone_number if not \
                            obj.user_settings.hide_phone_number else None
                representation['profile_pic'] = representation['profile_pic'] if not \
                            obj.user_settings.hide_photo else None
            else:
                return []
        return representation

class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    status = serializers.CharField(required=False)

class UserRegistrationSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True)
    phone_number = serializers.CharField()
    username = serializers.CharField()

    def validate(self, validated_data):
        otp = validated_data.pop('otp')
        username = validated_data.pop('username')
        phone_number = validated_data.get('phone_number')
        
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('User with this phone number does not exist.')
        
        try:
            user = CustomUser.objects.get(username=username)
            raise serializers.ValidationError('User with this username already exists.')
        except CustomUser.DoesNotExist:
            pass
        
        if not user.otp_secret == otp:
            raise serializers.ValidationError('Invalid OTP')
        user.username = username
        user.is_active = True
        user.save()
        validated_data['user'] = user

        return validated_data
    
class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

class ProfilePictureUpdateSerializer(serializers.Serializer):
    profile_pic = serializers.ImageField()

    def update(self, obj, validated_data):
        obj.profile_pic = validated_data.get('image', obj.profile_pic)
        obj.save()
        return obj
from rest_framework import serializers
from users.serializers import UserSerializer
from users.models import UserSettings

class UpdateUserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ["hide_phone_number", "hide_photo", "hide_online"]


class UserSettingsSerializer(serializers.ModelSerializer):
    blocked_users = serializers.SerializerMethodField()

    def get_blocked_users(self, obj):
        request = self.context['request']
        blocked_users = obj.blocked_users.all()
        return UserSerializer(blocked_users, many=True, context={'self': False, 'request': request}).data

    class Meta:
        model = UserSettings
        fields = '__all__'
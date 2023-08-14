from rest_framework import serializers
from social_app.models import *


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    password = serializers.CharField(min_length=8)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'full_name')

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ("id", "sender_id", "receiver_id", "accepted", "rejected", "updated_time")

class SentRequestSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField()

class FriendSerializer(serializers.ModelSerializer):
    friend_name = serializers.ReadOnlyField(source="friend.full_name")
    class Meta:
        model = Friends
        fields = ("id", "friend_id", "friend_name", "friendship_date")

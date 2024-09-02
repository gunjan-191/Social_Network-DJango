from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser , FriendRequest

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'name') 
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid login credentials')
        return {'user': user}


class UserSearchSerializer(serializers.Serializer):
    search_keyword = serializers.CharField()

    def validate_search_keyword(self, value):
        if not value:
            raise serializers.ValidationError("Search keyword cannot be empty.")
        return value
    
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name']
    
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['sender', 'receiver', 'status']

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name']
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from ..models import User, Otp


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'last_login', 'is_superuser', 'first_name', 'last_name', 'is_staff', 'is_active',
                  'date_joined', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class OtpSerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = ['id', 'user_id', 'code']
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenVerifySerializer,
)
from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [
            "password",
            "is_superuser",
            "is_staff",
            "is_active",
        ]
        depth = 1


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        user_serializer = UserSerializer(user)
        token['user'] = user_serializer.data
        return token


class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        from jwt import decode as jwt_decode
        from django.conf import settings
        super().validate(attrs)
        user_id = jwt_decode(attrs.get('token'), settings.SECRET_KEY, algorithms=[
                             'HS256'])['user']['id']
        if user_id:
            user = User.objects.get(id=user_id)
            return {"current_user": UserSerializer(user).data}

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListAPIView
from users.serializers import (
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    CustomTokenVerifySerializer,
)
from users.models import UserProfile
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User


class UsersListView(ListAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class CustomTokenVerifyView(TokenVerifyView):
    serializer_class = CustomTokenVerifySerializer